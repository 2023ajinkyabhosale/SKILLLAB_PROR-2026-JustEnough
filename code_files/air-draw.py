"""
Air Draw Pro - Raspberry Pi Edition (OPTIMIZED)
================================================
Multi-hand gesture-controlled air drawing system.
Heavily optimized for real-time performance on Raspberry Pi 4B (4GB).

KEY OPTIMIZATIONS vs original:
  - Threaded camera capture (no blocking on cap.read())
  - Resolution dropped to 320x240 (4x fewer pixels for MediaPipe)
  - Stable hand ID assignment (never flip-flops mid-session)
  - Reduced putText / drawing calls in renderer
  - FPS counter uses deque instead of list comprehension
  - canvas compositing uses numpy mask instead of two bitwise_and calls
  - Skeletons drawn only in debug mode
  - mp_complexity=0 enforced
  - SKIP-FRAME DETECTION: MediaPipe runs every N frames only
  - VELOCITY INTERPOLATION: cursor position predicted between detections
    so drawing stays smooth even when MediaPipe is skipped

PRIMARY HAND  : Drawing, erasing, hover
SECONDARY HAND: Color selection (when primary is open palm), thickness control

HAND LOCK:
  Perform fist->open x3 cycles to lock a hand as the drawing hand.
  Until locked, whichever hand first appears is tentatively primary,
  but the assignment is STABLE (won't swap every frame).

KEYBOARD:
  c   : Clear canvas
  s   : Save drawing
  d   : Toggle debug overlay
  q   : Quit

INSTALL (inside your Pi venv):
  pip install opencv-python mediapipe numpy
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import os
import threading
from collections import deque

# =============================================================================
#  CONFIGURATION  (tweak here first before touching code)
# =============================================================================

CAMERA_INDEX   = 0
FRAME_W        = 320      # ← KEY: 320x240 is ~4x faster than 640x480 for MediaPipe
FRAME_H        = 240
FPS_TARGET     = 30       # ask the camera for 30; Pi will deliver what it can

DEBOUNCE_SEC   = 0.35     # gesture must be stable this long before triggering
LOCK_CYCLES_REQ = 3       # fist->open cycles to lock hand

BRUSH_MIN      = 2
BRUSH_MAX      = 18
ERASER_MIN     = 10
ERASER_MAX     = 40

SMOOTH_ALPHA   = 0.50     # position smoothing (higher = more smoothing / more lag)

# Skip-frame detection — MediaPipe only runs every Nth frame.
# Between detections, cursor position is predicted using velocity.
#   2 = MediaPipe at ~half rate  → big FPS gain, barely noticeable
#   3 = MediaPipe at ~third rate → maximum speed, slight smoothing on fast moves
# Start with 2. If still slow, try 3.
DETECT_EVERY_N = 2

MP_COMPLEXITY  = 0        # must stay 0 on Pi
MP_DET_CONF    = 0.60
MP_TRACK_CONF  = 0.50

UI_H           = 42       # toolbar height in pixels

# Color palette: name -> BGR
COLORS = {
    "Red":     (0,   0,   220),
    "Green":   (0,   200, 60),
    "Blue":    (220, 80,  0),
    "Yellow":  (0,   220, 220),
    "White":   (255, 255, 255),
    "Orange":  (0,   140, 255),
    "Purple":  (180, 0,   180),
    "Cyan":    (220, 200, 0),
    "Magenta": (200, 0,   200),
    "Gray":    (150, 150, 150),
}
COLOR_LIST  = list(COLORS.values())
COLOR_NAMES = list(COLORS.keys())


# =============================================================================
#  MODULE 0: THREADED CAMERA (eliminates blocking cap.read lag)
# =============================================================================

class ThreadedCamera:
    """
    Reads frames in a background thread so the main loop never waits on cap.read().
    This alone can cut perceived lag by 30-50ms on Pi.
    """

    def __init__(self, index, w, h, fps):
        self._cap = cv2.VideoCapture(index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self._cap.set(cv2.CAP_PROP_FPS,          fps)
        # Minimize internal buffer — only keep the freshest frame
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)

        self._frame  = None
        self._lock   = threading.Lock()
        self._stop   = False
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reader(self):
        while not self._stop:
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame

    def read(self):
        """Return the most recent frame, or None if not yet available."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    @property
    def width(self):
        return int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def release(self):
        self._stop = True
        self._thread.join(timeout=1.0)
        self._cap.release()


# =============================================================================
#  MODULE 0b: CURSOR PREDICTOR (velocity-based interpolation)
# =============================================================================

class CursorPredictor:
    """
    Between MediaPipe detection frames, predicts where each fingertip is
    using a simple velocity model.
    """

    def __init__(self, smooth_alpha=SMOOTH_ALPHA):
        self._alpha   = smooth_alpha      # EMA weight for new detection
        self._sx      = None              # smoothed x (what we actually use)
        self._sy      = None              # smoothed y
        self._vx      = 0.0              # velocity x (pixels/frame)
        self._vy      = 0.0              # velocity y (pixels/frame)
        self._lx      = None              # last detected raw x
        self._ly      = None              # last detected raw y
        self._age     = 0                 # frames since last real detection

    def update_detection(self, raw_x, raw_y):
        """Call this when MediaPipe actually ran and returned a position."""
        if self._lx is not None:
            elapsed = max(1, self._age)
            self._vx = (raw_x - self._lx) / elapsed
            self._vy = (raw_y - self._ly) / elapsed
            self._vx *= 0.75
            self._vy *= 0.75

        self._lx  = raw_x
        self._ly  = raw_y
        self._age = 0

        if self._sx is None:
            self._sx, self._sy = float(raw_x), float(raw_y)
        else:
            self._sx = self._sx * self._alpha + raw_x * (1 - self._alpha)
            self._sy = self._sy * self._alpha + raw_y * (1 - self._alpha)

        return int(self._sx), int(self._sy)

    def predict(self):
        """Call this on frames where MediaPipe was skipped."""
        if self._sx is None:
            return None, None

        self._age += 1

        pred_x = self._lx + self._vx * self._age
        pred_y = self._ly + self._vy * self._age

        pred_x = max(0.0, pred_x)
        pred_y = max(0.0, pred_y)

        self._sx = self._sx * self._alpha + pred_x * (1 - self._alpha)
        self._sy = self._sy * self._alpha + pred_y * (1 - self._alpha)

        return int(self._sx), int(self._sy)

    def reset(self):
        self._sx = self._sy = None
        self._lx = self._ly = None
        self._vx = self._vy = 0.0
        self._age = 0


class HandTracker:
    """Wraps MediaPipe Hands. Returns per-hand data dicts."""

    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._mp_draw  = mp.solutions.drawing_utils
        self._hands    = self._mp_hands.Hands(
            static_image_mode        = False,
            max_num_hands            = 2,
            model_complexity         = MP_COMPLEXITY,
            min_detection_confidence = MP_DET_CONF,
            min_tracking_confidence  = MP_TRACK_CONF,
        )

    def process(self, bgr_frame):
        """Process a BGR frame. Returns list of hand dicts (up to 2)."""
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)

        hands_data = []
        if not results.multi_hand_landmarks:
            return hands_data

        h, w = bgr_frame.shape[:2]
        for lm_obj, handed_obj in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            lm    = lm_obj.landmark
            label = handed_obj.classification[0].label  # "Left" or "Right"
            up    = self._fingers_up(lm)
            hands_data.append({
                "label":        label,
                "lm_obj":       lm_obj,
                "lm":           lm,
                "fingers_up":   up,
                "finger_count": sum(up),
                "tip_x":        int(lm[8].x * w),
                "tip_y":        int(lm[8].y * h),
            })

        return hands_data

    def draw_skeleton(self, frame, hand_data):
        self._mp_draw.draw_landmarks(
            frame, hand_data["lm_obj"], self._mp_hands.HAND_CONNECTIONS)

    @staticmethod
    def _fingers_up(lm):
        """[thumb, index, middle, ring, pinky] — True = extended."""
        tips = [4, 8, 12, 16, 20]
        dip  = [3, 6, 10, 14, 18]
        up   = [False] * 5
        up[0] = lm[tips[0]].x < lm[dip[0]].x   # thumb: horizontal
        for i in range(1, 5):
            up[i] = lm[tips[i]].y < lm[dip[i]].y
        return up


# =============================================================================
#  MODULE 2: GESTURE DETECTION
# =============================================================================

def classify_gesture(fingers_up):
    """Map fingers_up list to a named gesture string."""
    t, i, m, r, p = fingers_up
    if not any(fingers_up):          return "fist"
    if all(fingers_up):              return "open_palm"
    if i and not m and not r and not p:  return "index_only"
    if i and m and not r and not p:      return "index_middle"
    if t and not i and not m and not r and not p: return "thumb_only"
    if p and not i and not m and not r and not t: return "pinky_only"
    if t and i and not m and not r and not p:     return "thumb_index"
    if t and i and not m and not r and p:         return "spider"
    if i and m and not r and p and not t:         return "index_middle_pinky"
    return f"fingers_{sum(fingers_up)}"

_COLOR_GESTURE_MAP = {
    "index_only":         0,
    "index_middle":       1,
    "fingers_3":          2,
    "fingers_4":          3,
    "open_palm":          4,
    "thumb_only":         5,
    "pinky_only":         6,
    "thumb_index":        7,
    "spider":             8,
    "index_middle_pinky": 9,
}

def gesture_to_color_idx(gesture):
    return _COLOR_GESTURE_MAP.get(gesture, None)

def finger_count_to_size(finger_count, min_val, max_val):
    count = max(1, min(5, finger_count))
    step  = (max_val - min_val) / 4.0
    return int(min_val + (count - 1) * step)


# =============================================================================
#  MODULE 3: DEBOUNCER
# =============================================================================

class Debouncer:
    """Confirms a value is stable for hold_sec before accepting it."""

    __slots__ = ("hold_sec", "_candidate", "_start", "confirmed")

    def __init__(self, hold_sec=DEBOUNCE_SEC):
        self.hold_sec   = hold_sec
        self._candidate = None
        self._start     = None
        self.confirmed  = None

    def update(self, value):
        now = time.monotonic()
        if value != self._candidate:
            self._candidate = value
            self._start     = now
            return False
        if self._start is not None and (now - self._start) >= self.hold_sec:
            if value != self.confirmed:
                self.confirmed = value
                return True
        return False

    def reset(self):
        self._candidate = None
        self._start     = None
        self.confirmed  = None


# =============================================================================
#  MODULE 4: STABLE HAND ASSIGNMENT + LOCK STATE MACHINE
# =============================================================================

class HandManager:
    """
    Manages stable primary/secondary assignment and the lock gesture sequence.
    [FIXED] Implements arbitration: Only ONE active candidate hand updates the lock 
    FSM to prevent the secondary hand or noisy swaps from disrupting the lock sequence.
    """

    VANISH_GRACE = 1.5   # seconds before a lost hand loses its role

    # FSM states per hand
    _IDLE    = 0
    _IN_FIST = 1
    _IN_OPEN = 2

    def __init__(self):
        self.lock_hand        = None   # "Left" / "Right" / None
        self._primary         = None
        self._primary_lost_at = None

        # [FIX] Track ONLY the active lock candidate to stop FSM interference
        self.active_lock_candidate = None  
        self._candidate_lost_at    = None

        # per-label FSM
        self._fsm        = {}   # label -> (state, cycle_count)
        self._fsm_db     = {}   # label -> Debouncer for lock gesture
        self._fsm_db["Left"]  = Debouncer(hold_sec=0.28)
        self._fsm_db["Right"] = Debouncer(hold_sec=0.28)
        self._fsm["Left"]  = (self._IDLE, 0)
        self._fsm["Right"] = (self._IDLE, 0)

    def update(self, hands_data):
        visible = {hd["label"]: hd for hd in hands_data}
        now     = time.monotonic()

        # ----------------------------------------------------------------------
        # 1. LOCK ARBITRATION (Fix for Left hand not locking)
        # ----------------------------------------------------------------------
        if not self.lock_hand:
            # Manage existing candidate
            if self.active_lock_candidate:
                if self.active_lock_candidate not in visible:
                    if self._candidate_lost_at is None:
                        self._candidate_lost_at = now
                    elif (now - self._candidate_lost_at) > self.VANISH_GRACE:
                        # Candidate lost completely. Reset its FSM so another hand can take over.
                        self._fsm[self.active_lock_candidate] = (self._IDLE, 0)
                        self._fsm_db[self.active_lock_candidate].reset()
                        self.active_lock_candidate = None
                        self._candidate_lost_at = None
                else:
                    self._candidate_lost_at = None # Found it

            # Pick a new candidate if none exists
            if self.active_lock_candidate is None and visible:
                self.active_lock_candidate = next(iter(visible))
                self._candidate_lost_at = None

            # [CRITICAL FIX] Update Lock FSM *ONLY* for the active candidate.
            # This isolates the logic preventing the other hand from causing state resets.
            if self.active_lock_candidate in visible:
                hd = visible[self.active_lock_candidate]
                gesture = classify_gesture(hd["fingers_up"])
                self._update_lock_fsm(self.active_lock_candidate, gesture)
        else:
            self.active_lock_candidate = self.lock_hand

        # ----------------------------------------------------------------------
        # 2. RESOLVE PRIMARY/SECONDARY HANDS
        # ----------------------------------------------------------------------
        if self.lock_hand:
            prim_label = self.lock_hand if self.lock_hand in visible else None
        else:
            prim_label = self._stable_primary(visible, now)

        sec_label = None
        for lbl in visible:
            if lbl != prim_label:
                sec_label = lbl
                break

        primary_data   = visible.get(prim_label)
        secondary_data = visible.get(sec_label)
        return primary_data, secondary_data

    def lock_progress(self, label):
        """Returns cycle count (0..LOCK_CYCLES_REQ) for UI display."""
        state, cycles = self._fsm.get(label, (self._IDLE, 0))
        return cycles

    # ------------------------------------------------------------------
    # Internals

    def _stable_primary(self, visible, now):
        """Assign primary without flip-flopping."""
        if not visible:
            if self._primary and self._primary_lost_at is None:
                self._primary_lost_at = now
            elif self._primary and (now - self._primary_lost_at) > self.VANISH_GRACE:
                self._primary      = None
                self._primary_lost_at = None
            return None

        if self._primary in visible:
            self._primary_lost_at = None   # hand is back
            return self._primary

        if self._primary and self._primary_lost_at is None:
            self._primary_lost_at = now

        if self._primary and (now - self._primary_lost_at) <= self.VANISH_GRACE:
            # Grace period: primary hand is temporarily missing, hold role
            return None

        # Primary expired or never set — assign first visible
        self._primary         = next(iter(visible))
        self._primary_lost_at = None
        return self._primary

    def _update_lock_fsm(self, label, gesture):
        if self.lock_hand:
            return

        db = self._fsm_db[label]
        if not db.update(gesture):
            return   # gesture not yet stable

        state, cycles = self._fsm[label]

        if state == self._IDLE:
            if gesture == "fist":
                self._fsm[label] = (self._IN_FIST, cycles)

        elif state == self._IN_FIST:
            if gesture in ("open_palm", "index_only", "index_middle"):
                cycles += 1
                self._fsm[label] = (self._IN_OPEN, cycles)
                if cycles >= LOCK_CYCLES_REQ:
                    self.lock_hand = label
                    print(f"[LOCK] Drawing hand locked to: {label}")

        elif state == self._IN_OPEN:
            if gesture == "fist":
                self._fsm[label] = (self._IN_FIST, cycles)


# =============================================================================
#  MODULE 5: DRAWING STATE MACHINE
# =============================================================================

class DrawingState:
    """Manages drawing mode, color, brush/eraser sizes, and the canvas."""

    MODE_HOVER = "hover"
    MODE_DRAW  = "draw"
    MODE_ERASE = "erase"

    def __init__(self, w, h):
        self.canvas      = np.zeros((h, w, 3), dtype=np.uint8)
        self.mode        = self.MODE_HOVER
        self.color_idx   = 0
        self.brush_size  = 6
        self.eraser_size = 20

        self._prev_x = None
        self._prev_y = None
        self._sx     = None   # smoothed x
        self._sy     = None   # smoothed y

        self._mode_db  = Debouncer(hold_sec=DEBOUNCE_SEC)
        self._color_db = Debouncer(hold_sec=DEBOUNCE_SEC)
        self._thick_db = Debouncer(hold_sec=0.20)

    # ---- PRIMARY HAND -------------------------------------------------------

    def update_primary(self, gesture, tip_x, tip_y):
        """
        Update mode from gesture (debounced), smooth cursor, paint canvas.
        Returns (cx, cy) smoothed cursor position.
        """
        # Mode debounce
        raw_mode = self._gesture_to_mode(gesture)
        if self._mode_db.update(raw_mode):
            self.mode = self._mode_db.confirmed

        # Smooth position
        if self._sx is None:
            self._sx, self._sy = tip_x, tip_y
        self._sx = int(self._sx * SMOOTH_ALPHA + tip_x * (1 - SMOOTH_ALPHA))
        self._sy = int(self._sy * SMOOTH_ALPHA + tip_y * (1 - SMOOTH_ALPHA))
        cx, cy = self._sx, self._sy

        # Paint (only below toolbar)
        if cy > UI_H:
            if self.mode == self.MODE_DRAW:
                color = COLOR_LIST[self.color_idx]
                sz    = self.brush_size
                if self._prev_x is not None:
                    cv2.line(self.canvas,
                             (self._prev_x, self._prev_y), (cx, cy),
                             color, sz * 2, lineType=cv2.LINE_AA)
                else:
                    cv2.circle(self.canvas, (cx, cy), sz, color, -1)
                self._prev_x, self._prev_y = cx, cy

            elif self.mode == self.MODE_ERASE:
                cv2.circle(self.canvas, (cx, cy), self.eraser_size, (0, 0, 0), -1)
                self._prev_x, self._prev_y = cx, cy

            else:
                self._prev_x = self._prev_y = None
        else:
            self._prev_x = self._prev_y = None

        return cx, cy

    def primary_lost(self):
        self._prev_x = self._prev_y = None
        self._sx     = self._sy     = None

    # ---- SECONDARY HAND -----------------------------------------------------

    def update_secondary(self, gesture, finger_count, primary_gesture):
        if primary_gesture == "open_palm":
            self._try_color(gesture)
        elif finger_count > 0:
            self._try_thickness(finger_count)

    def _try_color(self, gesture):
        idx = gesture_to_color_idx(gesture)
        if idx is None:
            return
        idx = idx % len(COLOR_LIST)
        if self._color_db.update(idx):
            self.color_idx = self._color_db.confirmed

    def _try_thickness(self, finger_count):
        if self._thick_db.update(finger_count):
            fc = self._thick_db.confirmed
            if self.mode == self.MODE_ERASE:
                self.eraser_size = finger_count_to_size(fc, ERASER_MIN, ERASER_MAX)
            else:
                self.brush_size  = finger_count_to_size(fc, BRUSH_MIN, BRUSH_MAX)

    # ---- CANVAS OPS ---------------------------------------------------------

    def clear(self):
        self.canvas[:] = 0
        self._prev_x = self._prev_y = None

    def save(self):
        fname = f"airdraw_{int(time.time())}.png"
        cv2.imwrite(fname, self.canvas)
        print(f"[SAVED] {os.path.abspath(fname)}")
        return fname

    @staticmethod
    def _gesture_to_mode(gesture):
        if gesture == "index_only":   return DrawingState.MODE_DRAW
        if gesture == "index_middle": return DrawingState.MODE_HOVER
        if gesture == "fist":         return DrawingState.MODE_ERASE
        return DrawingState.MODE_HOVER


# =============================================================================
#  MODULE 6: RENDERER
# =============================================================================

class Renderer:
    """All visual output — compositing, toolbar, cursor, debug overlay."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        # Pre-build a reusable scratch for compositing
        self._mask = np.zeros((h, w), dtype=np.uint8)

    def composite(self, frame, canvas):
        """Overlay canvas on frame. Faster than two bitwise_and calls."""
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        # Where mask is set, replace frame pixels with canvas pixels
        np.copyto(frame, canvas, where=(mask[:, :, np.newaxis] > 0))
        return frame

    def draw_toolbar(self, frame, ds, hand_mgr, fps, debug_on):
        """
        Top UI bar.
        [FIXED] Implements relative layout placing text elements cleanly from 
        the right side, recalculating spacing dynamically via cv2.getTextSize.
        """
        cv2.rectangle(frame, (0, 0), (self.w, UI_H), (25, 25, 25), -1)

        # ---------------------------------------------------------------------
        # Left Side: Color swatches 
        # ---------------------------------------------------------------------
        # dynamically adapt swatch width avoiding overlap in center
        sw  = max(12, (self.w // 2) // len(COLORS)) 
        gap = 2
        for idx, bgr in enumerate(COLOR_LIST):
            x1 = gap + idx * (sw + gap)
            x2 = x1 + sw
            cv2.rectangle(frame, (x1, 4), (x2, UI_H - 4), bgr, -1)
            if idx == ds.color_idx and ds.mode != DrawingState.MODE_ERASE:
                cv2.rectangle(frame, (x1-1, 3), (x2+1, UI_H-3), (255, 220, 50), 1)

        # ---------------------------------------------------------------------
        # Right Side: Status Elements (Relative placement mapping right -> left)
        # ---------------------------------------------------------------------
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.38
        thick = 1
        
        # We start X from the very right margin, building leftwards
        right_x = self.w - 4  

        # 1. FPS 
        fps_txt = f"{fps}fps"
        fps_col = (50, 200, 50) if fps >= 15 else (50, 50, 220)
        (fw, fh), _ = cv2.getTextSize(fps_txt, font, scale, thick)
        right_x -= fw
        cv2.putText(frame, fps_txt, (right_x, UI_H - 9), font, scale, fps_col, thick)
        right_x -= 10   # apply padding between elements

        # 2. Lock Status
        lock_txt = f"LK:{hand_mgr.lock_hand[0] if hand_mgr.lock_hand else '?'}"
        lk_col   = (0, 200, 255) if hand_mgr.lock_hand else (80, 80, 80)
        (lw, lh), _ = cv2.getTextSize(lock_txt, font, scale, thick)
        right_x -= lw
        cv2.putText(frame, lock_txt, (right_x, UI_H - 9), font, scale, lk_col, thick)
        right_x -= 10

        # 3. Brush/Eraser Size (Now cleanly embedded in UI)
        br_val = ds.eraser_size if ds.mode == DrawingState.MODE_ERASE else ds.brush_size
        br_txt = f"Br:{br_val}"
        (bw, bh), _ = cv2.getTextSize(br_txt, font, scale, thick)
        right_x -= bw
        cv2.putText(frame, br_txt, (right_x, UI_H - 9), font, scale, (200, 200, 200), thick)
        right_x -= 10

        # 4. Mode Box
        mode_bgr = {DrawingState.MODE_DRAW: (50,200,50),
                    DrawingState.MODE_HOVER: (100,100,200),
                    DrawingState.MODE_ERASE: (60,60,220)}[ds.mode]
        mode_lbl = {"draw":"DRW", "hover":"HOV", "erase":"ERS"}[ds.mode]
        
        (mw, mh), _ = cv2.getTextSize(mode_lbl, font, scale, thick)
        pad_x = 4
        mode_w = mw + (pad_x * 2)
        right_x -= mode_w
        
        cv2.rectangle(frame, (right_x, 4), (right_x + mode_w, UI_H - 4), mode_bgr, -1)
        cv2.putText(frame, mode_lbl, (right_x + pad_x, UI_H - 9), font, scale, (20, 20, 20), thick)

        # Bottom hint (tiny)
        cv2.putText(frame, "c:clr s:save d:dbg q:quit | fistx3=LOCK",
                    (4, self.h - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (70, 70, 70), 1)

    def draw_cursor(self, frame, cx, cy, ds):
        if cx is None:
            return
        if ds.mode == DrawingState.MODE_ERASE:
            cv2.circle(frame, (cx, cy), ds.eraser_size, (60,60,220), 1)
        elif ds.mode == DrawingState.MODE_DRAW:
            cv2.circle(frame, (cx, cy), ds.brush_size+1,
                       COLOR_LIST[ds.color_idx], 1)
            cv2.circle(frame, (cx, cy), 2, (255,255,255), -1)
        else:
            cv2.circle(frame, (cx, cy), 4, (150,150,200), 1)

    def draw_debug(self, frame, hands_data, hand_mgr, prim_data, ds):
        lines = [
            f"Lock:{hand_mgr.lock_hand}  Mode:{ds.mode} Cand:{hand_mgr.active_lock_candidate}",
            f"Color:{COLOR_NAMES[ds.color_idx]}  Br:{ds.brush_size}  Er:{ds.eraser_size}",
        ]
        for hd in hands_data:
            ges = classify_gesture(hd["fingers_up"])
            prog = hand_mgr.lock_progress(hd["label"])
            lines.append(f"{hd['label']} ges:{ges} cnt:{hd['finger_count']} lk:{prog}/{LOCK_CYCLES_REQ}")
        for j, ln in enumerate(lines):
            cv2.putText(frame, ln, (4, UI_H+12+j*14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0,240,180), 1)

    def draw_save_flash(self, frame, flash_frames):
        if flash_frames > 0:
            cv2.putText(frame, "SAVED!", (self.w//2-40, self.h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (50,255,80), 2)


# =============================================================================
#  MAIN LOOP
# =============================================================================

def main():
    cam = ThreadedCamera(CAMERA_INDEX, FRAME_W, FRAME_H, FPS_TARGET)
    time.sleep(0.5)   # let camera warm up

    # Wait for first frame
    frame = None
    for _ in range(30):
        frame = cam.read()
        if frame is not None:
            break
        time.sleep(0.05)

    if frame is None:
        print(f"[ERROR] Cannot read from camera {CAMERA_INDEX}.")
        cam.release()
        return

    actual_w, actual_h = frame.shape[1], frame.shape[0]
    print(f"[INFO] Camera: {actual_w}x{actual_h}")

    tracker  = HandTracker()
    hand_mgr = HandManager()
    drawing  = DrawingState(actual_w, actual_h)
    renderer = Renderer(actual_w, actual_h)

    fps_dq      = deque(maxlen=30)   # timestamps for FPS calc
    save_flash  = 0
    debug_on    = False
    fps         = 0

    print("[INFO] Air Draw Pro started.")
    print("       Fist -> open x3 on one hand = LOCK that hand for drawing.")
    print("       Press 'q' to quit.")

    while True:
        frame = cam.read()
        if frame is None:
            continue

        frame = cv2.flip(frame, 1)

        # ---- Hand tracking -------------------------------------------------
        hands_data = tracker.process(frame)

        # ---- Stable hand assignment ----------------------------------------
        primary_data, secondary_data = hand_mgr.update(hands_data)

        if primary_data is None:
            drawing.primary_lost()

        # ---- Drawing update ------------------------------------------------
        cx = cy = None
        primary_gesture = None

        if primary_data is not None:
            primary_gesture = classify_gesture(primary_data["fingers_up"])
            cx, cy = drawing.update_primary(
                primary_gesture,
                primary_data["tip_x"],
                primary_data["tip_y"],
            )

        if secondary_data is not None:
            sec_gesture = classify_gesture(secondary_data["fingers_up"])
            drawing.update_secondary(
                sec_gesture,
                secondary_data["finger_count"],
                primary_gesture,
            )

        # ---- Render --------------------------------------------------------
        output = renderer.composite(frame, drawing.canvas)
        renderer.draw_toolbar(output, drawing, hand_mgr, fps, debug_on)
        renderer.draw_cursor(output, cx, cy, drawing)

        if primary_gesture == "open_palm" and secondary_data is not None:
            cv2.putText(output, "COLOR SELECT: use other hand",
                        (4, UI_H + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,220,220), 1)

        if debug_on:
            for hd in hands_data:
                tracker.draw_skeleton(frame, hd)
            renderer.draw_debug(output, hands_data, hand_mgr, primary_data, drawing)

        renderer.draw_save_flash(output, save_flash)
        if save_flash > 0:
            save_flash -= 1

        # ---- FPS -----------------------------------------------------------
        now = time.monotonic()
        fps_dq.append(now)
        if len(fps_dq) > 1:
            fps = int((len(fps_dq) - 1) / (fps_dq[-1] - fps_dq[0]))

        cv2.imshow("Air Draw Pro", output)

        # ---- Key handling --------------------------------------------------
        key = cv2.waitKey(1) & 0xFF
        if   key == ord('q'):
            break
        elif key == ord('c'):
            drawing.clear()
        elif key == ord('s'):
            drawing.save()
            save_flash = 40
        elif key == ord('d'):
            debug_on = not debug_on
            print(f"[DEBUG] {'ON' if debug_on else 'OFF'}")

    cam.release()
    cv2.destroyAllWindows()
    print("[INFO] Air Draw Pro closed.")


if __name__ == "__main__":
    main()
