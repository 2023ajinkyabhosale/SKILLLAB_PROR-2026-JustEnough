"""
Air Draw - Raspberry Pi Edition
================================
Draw in the air using your index finger via webcam.
Uses MediaPipe for hand tracking + OpenCV for display.

GESTURES:
  ✏️  Index finger up only       → DRAW
  ✋  Index + Middle finger up    → HOVER (move without drawing)
  ✊  Fist / all fingers down     → ERASE mode toggle (hold 1 sec)

KEYBOARD SHORTCUTS:
  1-5   → Switch color
  +/-   → Brush size up/down
  c     → Clear canvas
  s     → Save drawing as PNG
  e     → Toggle eraser
  q     → Quit

INSTALL (on Raspberry Pi, inside your venv):
  pip install opencv-python mediapipe numpy
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import os

# ─────────────────────────────────────────────
#  CONFIG  (tweak these for your setup)
# ─────────────────────────────────────────────
CAMERA_INDEX    = 0          # try 1 if 0 doesn't work
FRAME_W         = 640        # lower = faster on Pi (try 480)
FRAME_H         = 480
FPS_TARGET      = 20         # Pi can handle ~20 fps comfortably
BRUSH_SIZE      = 6
ERASER_SIZE     = 40
SMOOTHING       = 0.4        # 0 = no smooth, 0.9 = very smooth (may lag)
DETECTION_CONF  = 0.7
TRACKING_CONF   = 0.6

# Color palette  (BGR)
COLORS = {
    "1 Red":     (0,   0,   220),
    "2 Green":   (0,   200, 60),
    "3 Blue":    (220, 80,  0),
    "4 Yellow":  (0,   220, 220),
    "5 White":   (255, 255, 255),
}
COLOR_LIST = list(COLORS.values())
COLOR_NAMES = list(COLORS.keys())

UI_BG       = (30, 30, 30)
UI_ACTIVE   = (255, 200, 50)
UI_TEXT     = (240, 240, 240)
CURSOR_CLR  = (180, 180, 180)

# ─────────────────────────────────────────────
#  MEDIAPIPE SETUP
# ─────────────────────────────────────────────
mp_hands    = mp.solutions.hands
mp_draw     = mp.solutions.drawing_utils
mp_styles   = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=DETECTION_CONF,
    min_tracking_confidence=TRACKING_CONF,
)

# ─────────────────────────────────────────────
#  CAMERA SETUP
# ─────────────────────────────────────────────
cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
cap.set(cv2.CAP_PROP_FPS, FPS_TARGET)

if not cap.isOpened():
    print(f"[ERROR] Cannot open camera index {CAMERA_INDEX}")
    print("        Try changing CAMERA_INDEX to 1 or 2 at the top of the script.")
    exit(1)

# ─────────────────────────────────────────────
#  STATE
# ─────────────────────────────────────────────
canvas          = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
color_idx       = 0
brush_size      = BRUSH_SIZE
eraser_mode     = False
prev_x, prev_y  = None, None   # smoothed position
raw_x,  raw_y   = None, None
fist_start      = None
save_flash      = 0             # frames to show "SAVED" message
fps_counter     = []

UI_H = 60  # height of top toolbar


def fingers_up(lm, w, h):
    """Return list of which fingers are extended: [thumb, index, middle, ring, pinky]"""
    tips  = [4, 8, 12, 16, 20]
    base  = [3, 6, 10, 14, 18]
    up    = []
    # Thumb: compare x
    if lm[4].x < lm[3].x:   # right hand; flip for left
        up.append(True)
    else:
        up.append(False)
    # Other 4: tip.y < base.y  →  finger up
    for t, b in zip(tips[1:], base[1:]):
        up.append(lm[t].y < lm[b].y)
    return up


def draw_ui(frame, color_idx, brush_size, eraser_mode, fps):
    """Draw the top toolbar."""
    # Background bar
    cv2.rectangle(frame, (0, 0), (FRAME_W, UI_H), UI_BG, -1)

    # Color swatches
    swatch_w = 48
    for i, (name, bgr) in enumerate(COLORS.items()):
        x1 = 10 + i * (swatch_w + 6)
        y1, y2 = 8, UI_H - 8
        x2 = x1 + swatch_w
        cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, -1)
        if i == color_idx and not eraser_mode:
            cv2.rectangle(frame, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), UI_ACTIVE, 3)
        cv2.putText(frame, name[0], (x1 + 16, y2 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)

    # Eraser indicator
    e_x = 10 + len(COLORS) * (swatch_w + 6) + 10
    e_label = "ERASE" if eraser_mode else " [e] "
    e_color = (80, 80, 255) if eraser_mode else (100, 100, 100)
    cv2.rectangle(frame, (e_x, 8), (e_x + 68, UI_H - 8), e_color, -1)
    cv2.putText(frame, e_label, (e_x + 4, UI_H - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, UI_TEXT, 1)

    # Brush size display
    bx = e_x + 80
    cv2.putText(frame, f"Sz:{brush_size}", (bx, UI_H - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, UI_TEXT, 1)

    # FPS
    cv2.putText(frame, f"FPS:{fps:2d}", (FRAME_W - 90, UI_H - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (140, 200, 140), 1)

    # Hint line
    cv2.putText(frame, "1-5:color  +/-:size  c:clear  s:save  e:erase  q:quit",
                (5, FRAME_H - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (120, 120, 120), 1)


print("[INFO] Air Draw started. Show your hand to the camera!")
print("       Press 'q' to quit.\n")

while True:
    t0 = time.time()
    ret, frame = cap.read()
    if not ret:
        print("[WARN] Frame drop — retrying…")
        continue

    frame = cv2.flip(frame, 1)  # mirror for natural feel
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    results = hands.process(rgb)
    rgb.flags.writeable = True

    gesture = "none"
    cx, cy  = None, None

    if results.multi_hand_landmarks:
        lm   = results.multi_hand_landmarks[0].landmark
        h, w = frame.shape[:2]
        up   = fingers_up(lm, w, h)

        # Raw tip of index finger
        ix = int(lm[8].x * w)
        iy = int(lm[8].y * h)

        # Smooth position
        if raw_x is None:
            raw_x, raw_y = ix, iy
        raw_x = int(raw_x * SMOOTHING + ix * (1 - SMOOTHING))
        raw_y = int(raw_y * SMOOTHING + iy * (1 - SMOOTHING))
        cx, cy = raw_x, raw_y

        # Gesture decode
        # Only index up → DRAW
        if up[1] and not up[2] and not up[3] and not up[4]:
            gesture = "draw"
            fist_start = None
        # Index + middle up → HOVER
        elif up[1] and up[2]:
            gesture = "hover"
            fist_start = None
        # Fist → timer-based erase toggle
        elif not any(up[1:]):
            gesture = "fist"
            if fist_start is None:
                fist_start = time.time()
            elif time.time() - fist_start > 1.0:
                eraser_mode = not eraser_mode
                fist_start = time.time()   # reset so it doesn't keep toggling
        else:
            fist_start = None

        # Draw skeleton on frame (lightweight style)
        mp_draw.draw_landmarks(
            frame,
            results.multi_hand_landmarks[0],
            mp_hands.HAND_CONNECTIONS,
            mp_styles.get_default_hand_landmarks_style(),
            mp_styles.get_default_hand_connections_style(),
        )

    # ── CANVAS OPERATIONS ──────────────────
    if cy is not None and cy > UI_H:   # don't draw inside toolbar area
        if gesture == "draw":
            color = (0, 0, 0) if eraser_mode else COLOR_LIST[color_idx]
            size  = ERASER_SIZE if eraser_mode else brush_size
            if prev_x is not None:
                cv2.line(canvas, (prev_x, prev_y), (cx, cy), color, size * 2,
                         lineType=cv2.LINE_AA)
            else:
                cv2.circle(canvas, (cx, cy), size, color, -1)
            prev_x, prev_y = cx, cy
        else:
            prev_x, prev_y = None, None
    else:
        prev_x, prev_y = None, None
        if cy is not None and gesture != "draw":
            # reset raw smoothing when hand leaves drawing area
            pass

    # ── COMPOSITE canvas + camera ──────────
    # Blend: where canvas has content, overlay it
    gray_canvas   = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask        = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY)
    mask_inv       = cv2.bitwise_not(mask)
    bg             = cv2.bitwise_and(frame, frame, mask=mask_inv)
    fg             = cv2.bitwise_and(canvas, canvas, mask=mask)
    combined       = cv2.add(bg, fg)

    # ── DRAW UI ────────────────────────────
    # FPS calc
    fps_counter.append(time.time())
    fps_counter = [t for t in fps_counter if time.time() - t < 1.0]
    fps = len(fps_counter)

    draw_ui(combined, color_idx, brush_size, eraser_mode, fps)

    # Cursor dot
    if cx is not None:
        cur_color = (0, 0, 180) if eraser_mode else COLOR_LIST[color_idx]
        cv2.circle(combined, (cx, cy), brush_size + 2, cur_color, 2)
        if eraser_mode:
            cv2.circle(combined, (cx, cy), ERASER_SIZE, (0, 0, 200), 2)

    # Gesture label (small, bottom-right)
    if gesture in ("draw", "hover", "fist"):
        label = {"draw": "DRAWING", "hover": "HOVER", "fist": "FIST (hold=erase)"}[gesture]
        cv2.putText(combined, label, (FRAME_W - 180, FRAME_H - 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 100), 1)

    # Save flash message
    if save_flash > 0:
        cv2.putText(combined, "SAVED!", (FRAME_W // 2 - 50, FRAME_H // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (50, 255, 50), 3)
        save_flash -= 1

    cv2.imshow("Air Draw - Raspberry Pi", combined)

    # ── KEY HANDLING ───────────────────────
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas[:] = 0
        prev_x, prev_y = None, None
    elif key == ord('s'):
        fname = f"airdraw_{int(time.time())}.png"
        cv2.imwrite(fname, canvas)
        print(f"[SAVED] {os.path.abspath(fname)}")
        save_flash = 40
    elif key == ord('e'):
        eraser_mode = not eraser_mode
    elif key in [ord(str(i)) for i in range(1, 6)]:
        color_idx   = int(chr(key)) - 1
        eraser_mode = False
    elif key == ord('+') or key == ord('='):
        brush_size = min(brush_size + 2, 40)
    elif key == ord('-'):
        brush_size = max(brush_size - 2, 2)

cap.release()
cv2.destroyAllWindows()
hands.close()
print("[INFO] Air Draw closed.")