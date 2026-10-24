import cv2
import time

# =========================
# 1. Load face detector
# =========================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# =========================
# 2. Camera init
# =========================
camera = cv2.VideoCapture(0)

# =========================
# 3. System states
# =========================
IDLE = 0
DETECTED = 1
OPEN = 2

state = IDLE

# smoothing / debounce
face_counter = 0

# timing control
last_detection_time = 0
DOOR_TIMEOUT = 6  # seconds (after no face -> close door)

print("=== Smart Door System v2 Activated ===")

try:
    while True:
        ret, frame = camera.read()
        if not ret or frame is None:
            continue

        current_time = time.time()

        # =========================
        # 4. Lightweight preprocessing
        # =========================
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

        # =========================
        # 5. Face detection (optimized)
        # =========================
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        # =========================
        # 6. Debounce logic
        # =========================
        if len(faces) > 0:
            face_counter += 1
            last_detection_time = current_time
        else:
            face_counter -= 1

        face_counter = max(0, min(face_counter, 5))

        # =========================
        # 7. State Machine
        # =========================
        if state == IDLE:
            if face_counter >= 2:
                state = OPEN
                print("🟢 DOOR OPENED (person detected)")

        elif state == OPEN:
            # timeout close logic
            if current_time - last_detection_time > DOOR_TIMEOUT:
                state = IDLE
                face_counter = 0
                print("🔴 DOOR CLOSED (timeout - no person)")

        # =========================
        # 8. UI overlay
        # =========================
        if state == OPEN:
            cv2.putText(
                frame,
                "DOOR OPEN",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.imshow("Smart Door System v2", frame)

        # =========================
        # 9. Exit control
        # =========================
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("System stopped by user.")
            break

finally:
    camera.release()
    cv2.destroyAllWindows()