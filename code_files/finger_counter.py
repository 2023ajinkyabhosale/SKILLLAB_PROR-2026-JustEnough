import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import urllib.request
import os

# ---------------------------------------------------------------------------
# Download the hand landmark model if it isn't already present
# ---------------------------------------------------------------------------
MODEL_PATH = "hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    url = (
        "https://storage.googleapis.com/mediapipe-models/"
        "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    )
    print("Downloading hand landmark model (~5 MB) ...")
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Download complete.\n")

# ---------------------------------------------------------------------------
# Landmark indices
# ---------------------------------------------------------------------------
TIP_IDS = [8, 12, 16, 20]   # index, middle, ring, pinky tips
PIP_IDS = [6, 10, 14, 18]   # their PIP (mid) joints

# Hand skeleton connection pairs for manual drawing
CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17),
]


# ---------------------------------------------------------------------------
# Finger counting
# ---------------------------------------------------------------------------
def count_fingers(landmarks, handedness_label):
    """
    Count extended fingers for one hand.
    landmarks        — list of NormalizedLandmark objects
    handedness_label — "Left" or "Right" as seen on the mirrored screen
    """
    count = 0

    # Thumb folds sideways, so compare x-coords
    if handedness_label == "Right":
        if landmarks[4].x < landmarks[3].x:
            count += 1
    else:
        if landmarks[4].x > landmarks[3].x:
            count += 1

    # Other fingers: tip y above PIP y = finger extended
    for tip, pip in zip(TIP_IDS, PIP_IDS):
        if landmarks[tip].y < landmarks[pip].y:
            count += 1

    return count


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def draw_skeleton(frame, landmarks, w, h):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 210, 90), 2, cv2.LINE_AA)
    for pt in pts:
        cv2.circle(frame, pt, 5, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, pt, 5, (0, 150, 60),    1, cv2.LINE_AA)


def draw_number(frame, number, w, h):
    font      = cv2.FONT_HERSHEY_DUPLEX
    scale     = 4.0
    thickness = 7
    text      = str(number) if number > 0 else "-"

    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    x = (w - tw) // 2
    y = th + 40

    # Dark shadow for readability on any background
    cv2.putText(frame, text, (x + 4, y + 4),
                font, scale, (20, 20, 20), thickness + 6, cv2.LINE_AA)
    # White text
    cv2.putText(frame, text, (x, y),
                font, scale, (255, 255, 255), thickness, cv2.LINE_AA)


def draw_hint(frame, h):
    cv2.putText(frame, "Show fingers  |  Q to quit",
                (12, h - 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (170, 170, 170), 1, cv2.LINE_AA)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Build the hand landmarker in VIDEO mode for per-frame detection
    options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    frame_index = 0

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Mirror the frame so it feels natural
            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]

            # Convert to MediaPipe image format
            rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            # Timestamp must be strictly increasing (in milliseconds)
            frame_index += 1
            timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC)) or frame_index * 33

            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            total = 0

            if result.hand_landmarks:
                for landmarks, handedness in zip(
                    result.hand_landmarks, result.handedness
                ):
                    # MediaPipe's label is relative to the unflipped image,
                    # so invert it after our mirror flip
                    raw_label = handedness[0].category_name
                    label     = "Left" if raw_label == "Right" else "Right"

                    total += count_fingers(landmarks, label)
                    draw_skeleton(frame, landmarks, w, h)

            total = min(total, 10)

            draw_number(frame, total, w, h)
            draw_hint(frame, h)

            cv2.imshow("Finger Counter  |  1 - 10", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
