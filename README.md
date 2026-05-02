# SKILL LAB PRATICAL HACKATHON

## Final Project README

> **Project Weight:** 100%  
> **Team Size:** 4/3 students  
> **Project Duration:** 16 hours  
> **Total Time Available:** 32 effort-hours per team  
> **Project Type:** Playful, interactive, technology-based experience

---

# Before you begin

## Fork and rename this repository

After forking this repository, rename it using the format:

`SKILLLAB_PROR-2026-TeamName`

### Example

`SKILLLAB_PROR-2026-AuroWizards`

Do not keep the default repository name.

---

# How to use this README

This file is your team’s **working project document**.

You must keep updating it throughout the build period.  
By the final review, this README should clearly show:

- your idea,
- your planning,
- your design decisions,
- your technical process,
- your build progress,
- your testing,
- your failures and changes,
- your final outcome.

## Rules

- Fill every section.
- Do not delete headings.
- If something does not apply, write `Not applicable` and explain why.
- Add images, screenshots, sketches, links, and videos wherever useful.
- Update task status and weekly logs regularly.
- Use this file as evidence of process, not only as a final report.

---

# 1. Team Identity

## 1.1 Studio / Group Name

`JustEnough`

## 1.2 Team Members

| Name                  | Primary Role                    | Secondary Role   | Strengths Brought to the Project |
| --------------        | ------------------------------- | --------------   | -------------------------------- |
| `Ajinkya Bhosale` | `Research  ` | `Coding and debugging`  | `Documentation, Hardware`|
| `Paras Dharmadhikari` | `Electronics / Coding `   | `ML model training`       | `Python, Linux`  |
| `Abhavya Verma`        | `ML model training`   | `Coding and debugging`       | `ML, Documentation`    |

## 1.3 Project Title

`"Air Drawing Through Hand Gestures"`

`(because Project-or)`

<img width="1600" height="1131" alt="image" src="https://github.com/user-attachments/assets/c64bfbd4-b3b7-43d9-83ad-c203a5aa11bc" />

## 1.4 One-Line Pitch

`Turn mid-air gestures into living digital art—where your hand becomes the brush and space itself the canvas.`

## 1.5 Expanded Project Idea

**Response:**  
An air-drawing system built on a Raspberry Pi 4 and a webcam that enables users to create digital artwork through mid-air hand gestures. The system captures and tracks hand movements in real time, translating them into precise strokes on a virtual canvas, effectively transforming the user’s hand into a contactless drawing tool. This creates an intuitive, immersive, and visually engaging interaction model that reimagines traditional input methods.

The project leverages computer vision techniques using OpenCV and hand-tracking frameworks such as MediaPipe to detect and interpret finger positions and motion. These inputs are processed on-device to render dynamic drawings, with support for gesture-based controls like color selection and brush modulation, demonstrating a modern approach to human–computer interaction. 

---

# 2. Inspiration

## 2.1 References

List what inspired the project.

| Source Type | Title / Link                                                        | What Inspired You                                                                         |
| ----------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `[Video]`   | `https://www.youtube.com/shorts/8hZK73xspEk` | `We happened to observe the whiteboard and thought what if we could draw on it through gestures.` |
|             |                                                                     |                                                                                           |
|             |                                                                     |                                                                                           |

## 2.2 Original Twist

What makes your project original?

**Response:**  
What makes this project stand out is that it goes beyond basic gesture control and focuses on creativity. Instead of just using gestures to trigger actions, it lets users freely draw in the air, making the interaction feel more natural and expressive. Features like gesture-based color and brush control also remove the need for any physical input.
Another key aspect is that it runs in real time on a Raspberry Pi 4, which adds a practical challenge and makes the system more efficient. Overall, it’s a simple idea but implemented in a way that feels interactive, modern, and actually useful, using tools like OpenCV and MediaPipe.

---

# 3. Project Intent

## 3.1 User Journey 

Describe exactly how a user will use the project.Make it a story
**Response:**  

Riya walks up to the setup — a webcam, a Raspberry Pi, and a canvas projected on the wall. No stylus, no touchscreen, nothing to pick up. She raises her index finger and a dot appears on the canvas. She moves her hand slowly to the left — a line follows. She keeps going, curving upward, looping back. She's drawing a bird. In the air. With her finger.
 
She uses her other hand — the color shifts. She draws the sun in the corner. She makes a fist and spreads her palm open and holds it flat — the canvas clears. She grins and starts over.
 
Five minutes in, she hasn't touched a single surface. The system just watched her hand and did the rest.
                                                  |



---

# 4. Definition of Success

## 4.1 Definition of “Usable”

The system reliably detects a user's hand, tracks the index fingertip, and renders continuous strokes on a visible canvas in real time — with no perceptible lag above ~800ms. A first-time user should be able to start drawing within 30 seconds of standing in front of it, with no instructions beyond "point your finger."


## 4.2 Minimum Usable Version

What is the smallest version of this project that still delivers the core experience?

**Response:**  

A webcam feed processed by MediaPipe on the Pi that maps the index fingertip position to a canvas and draws a continuous stroke as the finger moves. One gesture to clear the canvas (open palm, held for 1 second). No color switching, no brush control — just draw and clear. If someone can make a recognizable shape in the air, its enough to bring a smile on their face.

## 4.3 Stretch Features

What features are nice to have but not essential?

- Gesture-based color switching (pinch cycles through a palette)
- Save canvas as a PNG with a two-hand gesture
- Undo last stroke by drawing a quick circle in the air

---

# 5. System Overview

## 5.1 Project Type

Check all that apply.

- [ ] Electronics-based

- [ ] Mechanical

- [x] Sensor-based

- [ ] App-connected

- [ ] Motorized

- [ ] Sound-based

- [ ] Light-based

- [x] Screen/UI-based

- [ ] Fabricated structure

- [ ] Game logic based

- [ ] Installation

- [x] Software/AI based

## 5.2 High-Level System Description

**Input:** A Logitech USB webcam captures a continuous live video feed of the user's hand(s) positioned in front of it. No physical contact with any surface is required.

**Processing:** Each captured frame is mirrored horizontally and passed through MediaPipe's HandLandmarker model running locally on the Raspberry Pi 4B. The model detects up to two hands simultaneously, returning 21 landmarks per hand per frame. From these landmarks, the system determines which hand appeared first (assigned as the primary drawing hand), whether the primary hand's index finger is extended alone (draw mode) or all fingers are closed into a fist (erase mode), and how many fingers the secondary hand is showing (1–5), which instantly locks the corresponding color. All processing — model inference, gesture classification, canvas rendering, and display — runs in a single Python script directly on the Pi with no external servers or cloud calls.

**Output:** OpenCV maintains a persistent canvas buffer (a NumPy array) that accumulates strokes across frames. This canvas is composited over the live camera feed each frame and displayed on a connected HDMI monitor. A toolbar along the top edge shows the five color swatches, the active color, the current mode badge, and a live FPS counter.

**Physical structure:** The webcam is mounted on a small clip-stand positioned above and in front of the drawing zone. The Raspberry Pi 4B sits beside it, connected via HDMI to a monitor. The whole assembly sits on a single table with no moving mechanical parts.

**App interaction:** None. There is no companion app, no Wi-Fi dependency, and no external service. The system is entirely self-contained on the Pi.

## 5.3 Input / Output Map

| System Part | Signal / Data Type | Direction | What It Does |
|---|---|---|---|
| Logitech USB Webcam | Raw BGR video frames (320×240 @ ~30fps) | → Pi | Captures live hand position in the drawing zone |
| `cv2.flip(frame, 1)` | Mirrored BGR frame | Internal | Mirrors the image so hand movement feels natural |
| MediaPipe HandLandmarker | Landmark coordinates (x, y, z) × 21 × 2 hands | → Python | Identifies precise finger and joint positions per frame |
| `fingers_extended()` | Boolean list [thumb, index, middle, ring, pinky] | Internal | Determines which fingers are raised for each detected hand |
| Primary hand — index only | Fingertip pixel coords (landmark 8) | → Canvas | Draws a continuous stroke in the locked color |
| Primary hand — fist | Palm center pixel coords (landmark 9) | → Canvas | Erases a circular area of radius 18 px |
| Secondary hand — finger count | Integer 1–5 | → Draw Engine | Instantly locks the corresponding color |
| `DrawEngine.canvas` | NumPy uint8 array (H×W×3) | Internal | Persistent drawing surface; accumulates all strokes |
| `Renderer.composite()` | Merged BGR frame | → Display | Overlays canvas pixels onto the camera frame |
| HDMI Monitor | Final composited BGR frame | ← Pi | Displays the live augmented view to the user |
| Toolbar (OpenCV overlay) | Text + colored rectangles | ← Pi | Shows color swatches, active color, mode badge, FPS |
| Keyboard (`c`, `s`, `q`) | Key press events | → System | Clear canvas, save PNG, quit |

---

# 6. System Design, Sketches and Visual Planning

## 6.1 Concept Architecture / Sketch / Schematic

This section requires an uploaded image of your concept sketch. Below is the order of events your diagram should capture:

1. User stands in front of the webcam with hand raised
2. Webcam captures video and sends frames to the Pi over USB
3. Python script receives frames from the threaded camera buffer
4. Each frame is mirrored and converted to RGB for MediaPipe
5. HandLandmarker processes the frame and returns landmark data
6. Gesture classifier determines the mode (draw / erase) and color selection
7. Canvas is updated via OpenCV drawing calls
8. Canvas is composited over the raw camera frame
9. Final frame is rendered to the HDMI display with toolbar overlay
10. User sees their drawing appear in real time on screen

**Insert concept sketch / flow image below:**
`[Upload image and link here]`

## 6.2 Labeled Build Sketch / Architecture / Flow Diagram / Algorithm

Your labeled diagram should show the following elements with callouts:

- **Webcam** — positioned on a stand, pointing toward the user's hand zone
- **USB cable** — connecting webcam to Raspberry Pi USB 3.0 port
- **Raspberry Pi 4B** — central processing unit running the Python script
- **HDMI cable** — connecting Pi to the monitor
- **Monitor** — displaying the composited canvas output
- **Drawing zone** — the physical space in front of the webcam where the user gestures
- **Primary hand** — first detected hand; used for drawing and erasing
- **Secondary hand** — the other hand; used for color selection
- **Toolbar region** — top 44px of the display showing color swatches and mode badge

<img width="1600" height="1131" alt="image" src="https://github.com/2023ajinkyabhosale/SKILLLAB_PROR-2026-JustEnough/blob/main/images/rough_planning.jpeg" />


## 6.3 Approximate Dimensions

| Dimension | Value |
| --- | --- |
| Raspberry Pi 4B board length | 85 mm |
| Raspberry Pi 4B board width | 56 mm |
| Webcam (Logitech compact) width | ~65 mm |
| Webcam clip stand height | ~100 mm |
| Full table footprint (Pi + webcam + cables) | ~35 cm × 20 cm |
| Estimated total weight | ~280 g |

---

# 7. Electronics Planning

## 7.1 Electronics Used

| Component | Quantity | Purpose |
| --- | ---: | --- |
| Raspberry Pi 4B (4GB RAM) | 1 | Main compute unit — runs Python, MediaPipe, OpenCV, and drives display output |
| Logitech USB Webcam (compact, ~65mm) | 1 | Captures the live video feed; downscaled internally to 320×240 for performance |
| MicroSD Card (32GB, Class 10) | 1 | Storage for Raspberry Pi OS and all project files |
| USB-C Power Supply (5V / 3A) | 1 | Powers the Raspberry Pi 4B |
| Micro-HDMI to HDMI Cable | 1 | Connects Raspberry Pi to the external display |
| Monitor / External display | 1 | Shows the composited drawing canvas to the user |

## 7.2 Wiring Plan

The wiring for this project is minimal since the system is entirely software-driven with no custom electronics.

The **Logitech webcam** connects directly to one of the Raspberry Pi 4B's USB 3.0 ports via its built-in USB-A cable. No additional driver installation is needed — Raspberry Pi OS recognises it as `/dev/video0` automatically.

A **USB-C power supply (5V / 3A)** plugs into the Pi's USB-C power port. Using the official Raspberry Pi 4 power adapter or a certified equivalent is strongly recommended to avoid undervoltage warnings, which cause frame drops during processing.

A **Micro-HDMI to HDMI cable** connects the Pi's Micro-HDMI port (port 0, closest to the USB-C power jack) to the monitor's HDMI input.

No GPIO pins are used. No breadboard, no soldering — just three cables.

## 7.3 Circuit Diagram / Architecture Diagram

No custom circuit exists for this project. The connection topology is:

```
[USB-C Power Supply] ──USB-C──→ [Raspberry Pi 4B]
                                        │
                      USB-A (USB 3.0)   │   Micro-HDMI
                           ┌────────────┘─────────────────┐
                           ↓                              ↓
                  [Logitech USB Webcam]             [HDMI Monitor]
```


## 7.4 Power Plan

| Question | Response |
| --- | --- |
| Power source | USB-C mains adapter (wall power) |
| Voltage required | 5V DC |
| Current required | Minimum 3A |
| Peak draw estimate | ~2.5–2.8A under sustained MediaPipe inference load |
| Current concerns | The Pi 4B throttles if the supply cannot deliver 3A. The webcam draws an additional ~200mA over USB. An underpowered adapter will cause frame drops. |
| Safety concerns | No Li-ion batteries, no high voltages, no custom circuits. Standard mains safety at the wall outlet applies. Ensure the USB-C cable is rated for 3A. |

---

# 8. Software Planning

## 8.1 Software Tools

| Tool / Platform | Version / Notes | Purpose |
| --- | --- | --- |
| Python 3.11 | Pre-installed on Raspberry Pi OS (Bookworm) | Primary programming language |
| OpenCV (`opencv-python`) | 4.x | Camera capture, frame manipulation, canvas rendering, display output |
| MediaPipe (`mediapipe`) | 0.10.13 | Real-time hand landmark detection via the Tasks API (HandLandmarker) |
| NumPy | 1.x | Canvas buffer as a NumPy array; mask-based compositing |
| Raspberry Pi OS (64-bit) | Bookworm | Operating system; provides V4L2 webcam support out of the box |
| Python `threading` module | Standard library | Background webcam thread to eliminate blocking on `cap.read()` |
| Python `collections.deque` | Standard library | Rolling FPS calculation over the last 30 frame timestamps |

## 8.2 Software Logic / Algorithm

**Startup:** Initialize `ThreadedCamera` — a background thread reads frames continuously and stores only the most recent, removing blocking delay from `cap.read()`. Load the MediaPipe `HandLandmarker` model and instantiate `DrawEngine` (blank NumPy canvas) and `Renderer`.

**Per-frame loop:** Read the latest frame, mirror it with `cv2.flip(frame, 1)`, convert to RGB, and pass to `HandLandmarker.detect_for_video()` with a monotonically increasing timestamp.

**Hand assignment:** The first hand detected is assigned as primary and held stable until it fully disappears. The remaining visible hand (if any) is secondary. The thumb direction check is inverted based on MediaPipe's label to correct for the mirror flip, so both hands classify correctly.

**Gesture classification:**
- **Fist** (all fingers closed) → erase mode; cursor at landmark 9 (palm center)
- **Index only** → draw mode; cursor at landmark 8 (fingertip)
- **Any other shape** → pen lifted; previous-point memory reset

**Canvas update:** Draw mode: EMA-smoothed (`alpha = 0.5`) anti-aliased line from previous point to current, or a dot at stroke start. Erase mode: filled black circle of radius 18 px at palm center. Pen lifted: do not paint.

**Secondary hand — color:** Finger count (1–5) maps directly to the locked color: 1=Black, 2=Yellow, 3=Blue, 4=Green, 5=Red. A 30-frame flash confirms the selection.

**Rendering:** Canvas pixels are composited onto the camera frame via `np.copyto()` masking. The toolbar (color swatches, mode badge, FPS counter) and cursor overlay are drawn on top. `cv2.imshow()` outputs the final frame.

**Key handling:** `c` → clear canvas, `s` → save timestamped PNG, `q` → exit.

## 8.3 Code Flowchart

```
START
  └─ hand_landmarker.task exists? ──No──→ Download from CDN
  └─ ThreadedCamera: start background reader thread
  └─ Wait for first frame
  └─ Instantiate DrawEngine, Renderer, HandLandmarker
  └─ Open OpenCV window

LOOP (each frame)
  ├─ Read latest frame → flip horizontally
  ├─ Convert BGR → RGB → mp.Image
  ├─ HandLandmarker.detect_for_video(frame, timestamp)
  │
  ├─ HAND ASSIGNMENT
  │     └─ Assign/hold primary; remaining hand = secondary
  │
  ├─ PRIMARY HAND?
  │   ├─ YES → fingers_extended() → classify
  │   │         ├─ is_fist()       → erase_stroke(palm center)
  │   │         ├─ is_index_only() → draw_stroke(fingertip)
  │   │         └─ other           → lift_pen()
  │   └─ NO  → lift_pen()
  │
  ├─ SECONDARY HAND?
  │   ├─ YES → finger_count() in [1,5] → lock color, trigger flash
  │   └─ NO  → do nothing
  │
  ├─ RENDER
  │   ├─ composite(camera + canvas)
  │   ├─ draw_toolbar()
  │   ├─ draw_cursor()
  │   ├─ draw_color_flash() if active
  │   ├─ draw_hint()
  │   └─ cv2.imshow()
  │
  └─ KEY: c=clear  s=save  q=quit

END → cam.release() → cv2.destroyAllWindows()
```

<img width="1600" height="1131" alt="image" src="https://github.com/2023ajinkyabhosale/SKILLLAB_PROR-2026-JustEnough/blob/main/images/flowchart.jpeg" />

---

# 9. Bill of Materials

## 9.1 Full BOM

| Item | Quantity | In Kit? | Need to Buy? | Estimated Cost (₹) | Spec | Why This Choice? |
| --- | ---: | --- | --- | ---: | --- | --- |
| Raspberry Pi 4B (4GB RAM) | 1 | Yes | No | 0 | ARM Cortex-A72, 4GB LPDDR4, USB 3.0, Micro-HDMI | Sufficient compute for real-time MediaPipe inference at 320×240; USB 3.0 for low-latency webcam data |
| Logitech USB Webcam (compact, ~65mm) | 1 | No | Yes | 1,799 | Fixed focus, USB-A, ~65mm width | Plug-and-play on Pi OS, stable exposure, adequate frame rate for hand tracking |
| MicroSD Card (32GB, Class 10) | 1 | Yes | No | 0 | UHS-I | Pi OS and project file storage |
| USB-C Power Supply (5V / 3A) | 1 | Yes | No | 0 | Official Pi 4 adapter | Stable 3A delivery prevents throttling under MediaPipe load |
| Micro-HDMI to HDMI Cable | 1 | Yes | No | 0 | Standard 1m | Connects Pi to external display |

## 9.2 Material Justification

The Raspberry Pi 4B was the natural choice as the lowest-cost single-board computer capable of running MediaPipe's HandLandmarker in real time. Keeping input resolution at 320×240 rather than the webcam's native resolution reduces the pixel count by roughly four times — the single most impactful performance decision, more effective than any code-level optimisation.

The Logitech webcam was chosen over cheaper unbranded options because it is UVC-compliant and recognised by Pi OS without any driver configuration. Its fixed-focus lens is an advantage here — there is no autofocus hunting when a hand moves across the frame, and its stable auto-exposure keeps the hand visible under typical indoor lighting without manual tuning.

## 9.3 Items Procured

| Item | Why Needed | Purchase Source | Status |
| --- | --- | --- | --- |
| Raspberry Pi 4B (4GB RAM) | Main compute unit | In kit | Received |
| Logitech USB Webcam (compact, ~65mm) | Primary input device for hand tracking | Local electronics store / amazon.in | Received |
| MicroSD Card (32GB, Class 10) | Pi OS and project file storage | In kit | Received |
| USB-C Power Supply (5V / 3A) | Powers the Raspberry Pi 4B | In kit | Received |
| Micro-HDMI to HDMI Cable | Connects Pi to display | In kit | Received |

## 9.4 Budget Summary

| Budget Item | Estimated Cost (₹) |
| --- | ---: |
| Logitech USB Webcam | 1,799 |
| All other components (in kit) | 0 |
| **Total** | **1,799** |

## 9.5 Budget Reflection

The project is very low-cost because all compute and power hardware was already available in the lab kit. The only direct purchase was the webcam. There is no meaningfully cheaper webcam option that provides reliable plug-and-play compatibility on Pi OS with stable enough exposure for hand tracking — the Logitech range is the minimum reliable option at this price point.

---

# 10. Planning the Work

## 10.1 Team Working Agreement

**Task division:** Tasks are split by subsystem but ownership is shared — nobody is siloed. Paras leads coding and hardware integration, Ajinkya leads documentation, and Abhavya leads gesture logic and testing, but all three contribute across every area of the work.

**Decision making:** Decisions affecting more than one subsystem are made together. Smaller, contained decisions (like a smoothing factor or eraser radius) are made by whoever is working on that piece at the time and noted in the update log.

**Progress checks:** A quick sync at the start of each working session. Each person states what they finished, what they are working on, and whether anything is blocked. A block unresolved for more than one session gets the full group's attention.

**Delays:** If a task slips, we check if it is on the critical path. If yes, we pull someone from a non-critical task to help. If not, we adjust the deadline and note it in the update log.

**Documentation:** The README is updated continuously throughout the project, not filled in at the end. Whoever completes a task updates the relevant section the same day.

## 10.2 Task Breakdown

| Task ID | Task | Owner | Estimated Hours | Deadline | Dependency | Status |
| --- | --- | --- | ---: | --- | --- | --- |
| T1 | Finalise concept and confirm scope | All | 2 | Day 1 | None | Done |
| T2 | Set up Raspberry Pi OS, install Python dependencies | Paras | 2 | Day 1 | T1 | Done |
| T3 | Verify webcam feed at 320×240 on Pi, confirm MediaPipe model download | Paras | 1 | Day 1 | T2 | Done |
| T4 | Implement threaded camera and basic landmark detection loop | Paras | 3 | Day 1 | T3 | Done |
| T5 | Implement `fingers_extended()` with thumb-direction fix for both hands | Paras | 2 | Day 1 | T4 | Done |
| T6 | Implement draw stroke, erase stroke, canvas compositing | Abhavya | 3 | Day 1 | T5 | Done |
| T7 | Implement secondary-hand color selection (1–5 fingers) with flash feedback | Abhavya | 2 | Day 1 | T6 | Done |
| T8 | Implement toolbar renderer, mode badge, FPS counter, color swatches | Paras | 2 | Day 3 | T6 | Done |
| T9 | Save-to-PNG and clear canvas key bindings | Abhavya | 1 | Day 3 | T8 | Done |
| T10 | End-to-end testing on Pi: FPS, gesture accuracy, lighting conditions | All | 3 | Day 3 | T7, T9 | Done |
| T11 | Complete README documentation (sections 5–19) | Ajinkya | 3 | Day 3 | T10 | Done |

## 10.3 Responsibility Split

| Area | Main Owner | Support |
| --- | --- | --- |
| Concept and scope | All | — |
| Hardware setup and Pi OS | Paras | Ajinkya, Abhavya |
| MediaPipe integration and camera pipeline | Paras | Abhavya, Ajinkya |
| Gesture classification logic | Paras | Abhavya, Ajinkya |
| Drawing engine and canvas | Abhavya | Paras, Ajinkya |
| UI / Renderer / toolbar | Abhavya | Paras, Ajinkya |
| Testing and debugging | All | — |
| Documentation and README | Ajinkya | Abhavya, Paras |

---

# 11 Hour Milestones

## 11.1 8-Hour Plan

### Bi Hour 1 — Plan and De-risk

Expected outcomes:

- [x] Idea finalized
- [x] Core interaction decided
- [x] Sketches made
- [x] BOM completed
- [x] Purchase needs identified
- [x] Key uncertainty identified (MediaPipe performance on Pi at usable FPS)
- [x] Basic feasibility tested (landmark detection confirmed running on Pi)

### Bi Hour 2 — Build Subsystems

Expected outcomes:

- [x] Webcam feed confirmed at 320×240 on Pi
- [x] MediaPipe HandLandmarker returning landmarks in real time
- [x] Threaded camera implemented and reducing latency
- [x] `fingers_extended()` logic working correctly for both hands
- [x] Basic draw stroke appearing on canvas

### Bi Hour 3 — Integrate

Expected outcomes:

- [x] Full draw / erase / color-select pipeline connected end-to-end
- [x] Canvas composited over camera feed and displayed via HDMI
- [x] Toolbar rendering with correct active-color highlight
- [x] Secondary hand color selection locking correctly

### Bi Hour 4 — Refine and Finish

Expected outcomes:

- [x] FPS stable and acceptable under demo lighting
- [x] Cursor smoothing tuned (alpha = 0.5)
- [x] Save and clear key bindings working
- [x] README complete
- [x] Final build ready for demonstration

## 12.2 Update Log

| Days | Planned Goal | What Actually Happened | What Changed | Next Steps |
| --- | --- | --- | --- | --- |
| Day 1 | Pi setup, dependencies installed, webcam confirmed | Setup went smoothly. MediaPipe 0.10.35 did not work — `mp.solutions` API removed in newer versions. Had to switch to the Tasks API and download the `.task` model file. | Entire tracking module rewritten to use `vision.HandLandmarker` | Implement gesture classification on top of new API |
| Day 2 | Gesture classification, draw/erase working | Draw and erase both working. Left-hand thumb detection was inverted — after `cv2.flip()`, MediaPipe's label semantics are swapped. Fixed by inverting the thumb X-direction check based on the label. | `fingers_extended()` now takes label as a parameter | Connect secondary hand color selection |
| Day 3 | Color selection, toolbar, full pipeline | Color selection via finger count worked cleanly. Toolbar and FPS counter added. Eraser cursor moved from fingertip (landmark 8) to palm center (landmark 9) after it felt disconnected during testing. | Erase anchor changed from landmark 8 to landmark 9 | Full end-to-end testing, README |
| Day 4 | Testing, tuning, documentation | FPS on Pi was 8–10fps under standard lighting — workable for deliberate drawing. Smoothing alpha raised from 0.3 to 0.5 for cleaner lines. All three team members tested the system; interaction model was understood within a minute by each person. | Smoothing alpha tuned 0.3 → 0.5 | Final README, push to GitHub |

---

# 13. Risks and Unknowns

## 13.1 Risk Register

| Risk | Type | Likelihood | Impact | Mitigation Plan | Owner |
| --- | --- | --- | --- | --- | --- |
| MediaPipe FPS drops below acceptable level on Pi | Technical | Medium | High | Lock resolution to 320×240, use threaded camera, use float16 model with complexity=0 | Paras |
| Hand occlusion or background clutter causing mis-detection | Technical | Medium | Medium | Keep demo area behind the user reasonably uncluttered; point webcam at a plain or neutral background | Abhavya |
| Primary/secondary hand assignment swapping mid-drawing | Technical | Low | Medium | Primary hand persists across frames; only reassigned when it fully disappears | Abhavya |
| Pi undervolting and throttling under sustained load | Hardware | Low | High | Use official Pi 4 USB-C adapter rated for 3A | Paras |
| MediaPipe model download fails at demo (no internet) | Technical | Low | High | Pre-download `hand_landmarker.task` and commit it to the repo | Paras |

## 13.2 Biggest Unknown Right Now

The single biggest uncertainty is how the system performs under variable demo-room lighting. MediaPipe's hand detection degrades noticeably in low-contrast conditions — if the user's skin tone blends into a similarly lit background, landmark confidence drops and the hand may flicker in and out of detection mid-stroke, leaving broken lines on the canvas.

---

# 14. Testing

## 14.1 Technical Testing Plan

| What Needs Testing | How You Will Test It | Success Condition |
| --- | --- | --- |
| Webcam initialisation on Pi | Run script and check printed resolution output | Prints `[INFO] Camera: 320x240` with no errors |
| MediaPipe landmark detection | Show hand to camera; observe FPS and visual tracking | Landmarks track fingertips accurately at ≥8fps |
| Draw gesture (index only) | Extend only index finger and move hand | Continuous stroke follows fingertip |
| Erase gesture (fist) | Close all fingers and move hand | Black circle erases canvas where palm moves |
| Pen lift (neutral gesture) | Show two or three fingers (not index-only, not fist) | No stroke is drawn; previous stroke does not extend |
| Secondary hand color 1 (Black) | Show 1 finger on secondary hand | Black swatch highlights; next stroke is black |
| Secondary hand color 2 (Yellow) | Show 2 fingers | Yellow swatch highlights and locks |
| Secondary hand color 3 (Blue) | Show 3 fingers | Blue swatch highlights and locks |
| Secondary hand color 4 (Green) | Show 4 fingers | Green swatch highlights and locks |
| Secondary hand color 5 (Red) | Show 5 fingers / open palm | Red swatch highlights and locks |
| Clear canvas (`c` key) | Press `c` | Canvas immediately clears to black |
| Save PNG (`s` key) | Press `s` | `airdraw_<timestamp>.png` appears in working directory |
| Stable primary hand assignment | Draw with primary hand while occasionally showing secondary | Primary never swaps roles mid-stroke |

## 14.2 Testing and Debugging Log

| Date | Problem Found | Type | What You Tried | Result | Next Action |
| --- | --- | --- | --- | --- | --- |
| Day 1 | `AttributeError: module 'mediapipe' has no attribute 'solutions'` on 0.10.35 | Software | Tried downgrading to 0.10.9 — unavailable for Python 3.12 | Rewrote tracker using Tasks API on 0.10.13 | Confirmed working |
| Day 2 | Left-hand thumb detection inverted — fist not registering for left hand | Software | Printed `fingers_extended()` output for both hands | Thumb X-direction check must invert based on MediaPipe label | Added label parameter to `fingers_extended()`; fixed |
| Day 2 | Draw line connecting to (0,0) at start of each new stroke | Software | Checked `_prev_x` / `_prev_y` state | `lift_pen()` not called on mode switch — previous position persisted | Called `lift_pen()` on every non-draw/erase gesture |
| Day 3 | Eraser felt disconnected from hand when fist is closed | UX | Moved anchor from landmark 8 to landmark 9 | Significantly more natural | Kept |
| Day 4 | Slight jitter in drawn lines at fast movement | Software | Raised EMA smoothing alpha from 0.3 to 0.5 | Lines noticeably smoother with no perceptible lag | Kept at 0.5 |

## 14.3 Playtesting Notes

| Tester | What They Did | What Confused Them | What They Enjoyed | What You Will Change |
| --- | --- | --- | --- | --- |
| Ajinkya | Drew a house shape, tried all 5 colors | Initially unsure which hand was primary — no visual indicator on screen | Color flash feedback on switching; immediate response | Add a small label near the detected primary hand |
| Paras | Drew circles and tested erase precision | Switching colors while primary hand was mid-gesture occasionally lifted the pen | The erase gesture — closing a fist feels very natural and deliberate | Ensure secondary hand detection does not interfere with primary stroke continuity |
| Abhavya | Tried free-form drawing for ~3 minutes | Took about 30 seconds to understand the two-hand color model | Drew a recognizable shape within a minute; said the interaction felt intuitive once the model clicked | None — the core experience landed exactly as intended |

---

# 15. Build Documentation

## 15.1 Fabrication Process

This project has no mechanical fabrication. The build process was entirely software and hardware setup.

**Hardware assembly:**
The Raspberry Pi 4B was placed in a standard protective case. The Logitech webcam was mounted on its clip-stand and positioned approximately 60cm in front of the drawing zone at roughly chest level, angled slightly downward. The webcam was connected to the Pi's USB 3.0 port. The HDMI cable connected the Pi's Micro-HDMI port to the monitor. The USB-C power adapter was connected last.

**Software environment:**
Raspberry Pi OS (64-bit, Bookworm) was flashed to a 32GB microSD card. Python 3.11 was pre-installed. Three dependencies were installed: `opencv-python`, `mediapipe==0.10.13`, and `numpy`. The `hand_landmarker.task` model file was downloaded once and committed to the repository so no internet connection is required at demo time.

**Revisions:**
The most significant revision was rewriting the hand-tracking module from the `mp.solutions.hands` API to the Tasks API due to a MediaPipe version incompatibility on Python 3.12. The erase cursor anchor was moved from landmark 8 to landmark 9 after playtesting. Smoothing alpha was tuned from 0.3 to 0.5 based on observed line quality.

---

# 16. Build Photos

<img width="1600" height="1131" alt="image" src="https://github.com/2023ajinkyabhosale/SKILLLAB_PROR-2026-JustEnough/blob/main/images/test%20drawing%20one.jpeg" />
<img width="1600" height="1131" alt="image" src="https://github.com/2023ajinkyabhosale/SKILLLAB_PROR-2026-JustEnough/blob/main/images/test%20drawing%20two.jpeg" />
<img width="1600" height="1131" alt="image" src="https://github.com/2023ajinkyabhosale/SKILLLAB_PROR-2026-JustEnough/blob/main/images/paras_testing_code.jpeg" />
<img width="1600" height="1131" alt="image" src="https://github.com/2023ajinkyabhosale/SKILLLAB_PROR-2026-JustEnough/blob/main/images/WhatsApp%20Image%202026-04-30%20at%2015.33.17.jpeg" />

---

# 17. Final Outcome

## 17.1 Final Description

The final system is a real-time air-drawing application running entirely on a Raspberry Pi 4B with a Logitech USB webcam. A user stands in front of the webcam, raises their dominant hand, and draws in mid-air using their index finger. The stroke appears on a canvas composited over the live camera feed and displayed on a monitor. Closing the hand into a fist switches to a precision eraser that follows the palm. Holding up 1–5 fingers on the other hand instantly changes the drawing color between five options: black, yellow, blue, green, and red. No physical surface is touched at any point.

The application runs at 8–10fps on the Pi under standard indoor lighting — sufficient for deliberate freehand drawing. The canvas persists until cleared with the `c` key, and completed drawings can be saved as PNG files with `s`. The on-screen toolbar shows the active color, current mode, and live FPS at all times.

## 17.2 What Works Well

- The index-finger draw gesture is immediately intuitive — every person who tried it started drawing within 30 seconds with no prior instruction.
- The fist-to-erase mapping feels natural; the palm-center anchor makes the eraser feel physically grounded to the hand.
- The two-hand color selection model is clean — showing fingers on the secondary hand changes the color instantly with no mode-switching required.
- EMA smoothing at alpha=0.5 produces clean lines without noticeable lag.
- The system is entirely self-contained on the Pi with no internet, no app, and no external dependencies after the initial model download.

## 17.3 What Still Needs Improvement

- There is no visual indicator showing which hand is currently assigned as primary. New users sometimes pick the wrong hand first.
- At 8–10fps, fast hand movements can leave small gaps between stroke segments. A gap-fill algorithm connecting the last known point to the next would help.
- Brush size is fixed. A gesture or key shortcut to change thickness would improve expressiveness.
- The saved canvas PNG is at 320×240 pixels, which is low resolution. Rendering strokes to a larger virtual buffer would produce better output images.

## 17.4 What Changed From the Original Plan

The original concept used `mp.solutions.hands` and included a complex hand-locking state machine requiring three deliberate fist-open cycles to assign a drawing hand. This was replaced entirely — the lock mechanism was the source of most bugs, particularly with left-hand detection, and made the setup feel cumbersome. The final design simply assigns the first detected hand as primary and holds that stably. Simpler, faster, and more reliable.

The color palette was also reduced from ten to five. The ten-color version required complex secondary-hand gestures that were unreliable. Five colors mapped directly to finger count 1–5 are unambiguous — there is no gesture the system can misread.

The eraser was originally a toggle (one gesture in, another out). The final design is hold-to-erase: fist = erase, anything else = draw. This removed a state machine entirely and made the eraser feel like picking up and putting down a real eraser.

---

# 18. Reflection

## 18.1 Team Reflection

All three members contributed across every part of the project — hardware setup, coding, testing, and documentation. Paras drove the majority of the coding and integration work, Ajinkya drove documentation, and Abhavya contributed heavily across gesture logic, testing, and the drawing engine. In practice the division was fluid; whenever one area was blocked, others stepped in immediately.

The biggest slowdown was the MediaPipe API change on day one, which forced a full module rewrite. We recovered because the problem was isolated to one module and the rest of the codebase did not need to change. Time management was otherwise solid — short syncs at the start of each session kept the project on track without eating into build time.

Keeping the README updated throughout rather than at the end made the final submission significantly less stressful, and meant the update log reflects what actually happened rather than a reconstructed version of events.

## 18.2 Technical Reflection

**Coding:** Pinning dependency versions early is essential for a time-constrained project. MediaPipe's breaking API change between minor versions cost us a full session. The biggest single performance gain was dropping input resolution to 320×240 — more effective than any algorithmic optimisation.

**Integration:** The mirror flip changes the meaning of MediaPipe's "Left" and "Right" labels in a way that is not prominently documented. Understanding that the thumb check must invert based on label took longer than the one-line fix itself.

**Architecture:** Separating concerns into `DrawEngine`, `Renderer`, and the main loop made debugging straightforward. When the eraser anchor felt wrong in testing, we knew exactly which method to change without reading anything else.

## 18.3 Design Reflection

**Clarity:** The interaction model had to be describable in one sentence: "point to draw, fist to erase, other hand changes color." Any feature that made that sentence longer got pushed back.

**Delight:** The moment that resonated most with every tester was the very first stroke — seeing a line follow their finger with no contact. That happened in the first ten seconds and was enough to make everyone want to keep going. Everything else built on top of that.

**Iteration:** Three significant design reversals happened during the project. None felt like failures because each was caught through testing on the actual hardware rather than at the demo.

**Physical interaction:** Webcam position matters more than expected. Height and angle significantly affect detection quality. Setting up the mount correctly for the demo environment should be the first step at any new venue.

## 18.4 If You Had One More Hour

We would add a small visual indicator — a coloured dot or ring rendered on the camera feed — around whichever hand is currently assigned as primary. Every new user's first question was "which hand do I draw with?" A single visual cue would resolve that within the first second of use and make demonstrations to observers much clearer without any verbal explanation needed.

---

# 19. Final Submission Checklist

Before submission, confirm that:

- [x] Team details are complete
- [x] Project description is complete
- [x] Inspiration sources are included
- [x] Sketches are added
- [x] BOM is complete
- [x] Purchase list is complete
- [x] Budget summary is complete
- [x] Mechanical planning is documented if applicable
- [x] App planning is documented if applicable
- [x] Code flowchart is added
- [x] Task breakdown is complete
- [x] Weekly logs are updated
- [x] Risk register is complete
- [x] Testing log is updated
- [x] Playtesting notes are included
- [x] Build photos are included
- [x] Final reflection is written

