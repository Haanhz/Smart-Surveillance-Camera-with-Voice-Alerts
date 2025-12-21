import cv2
import threading
import time
import subprocess
import requests
from ultralytics import YOLO
from queue import Queue, Empty
import requests
import base64

# ---------------- CONFIG ----------------
FRAME_SIZE = (256, 256)
DETECT_EVERY_N = 30
SPEAK_INTERVAL = 3

# ---------------- GLOBAL ----------------
stop_event = threading.Event()
detect_queue = Queue(maxsize=3)
main_queue = Queue(maxsize=3)

# ---------------- TTS -------------------
def speak_async(text):
    threading.Thread(
        target=subprocess.call,
        args=(["espeak-ng", "-v", "en", text],),
        daemon=True
    ).start()


# ---------------- EVENT -----------------
def send_frame_event(frame, event_text="Person detected"):
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
    frame_b64 = base64.b64encode(buffer).decode('utf-8')

    data = {
        "event": event_text,
        "timestamp": time.time(),
        "frame": frame_b64
    }

    try:
        requests.post("http://192.168.1.168:5000/event", json=data, timeout=0.5)
    except Exception as e:
        print("Failed to send frame:", e)

# ---------------- DATA ------------------
class FrameData:
    def __init__(self, frame, frame_id):
        self.frame = frame
        self.frame_id = frame_id
        self.person_detected = False

# ---------------- CAMERA ----------------
def camera_thread(cap):
    frame_id = 0
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            stop_event.set()
            break

        frame = cv2.flip(frame, 1)

        try:
            detect_queue.put(FrameData(frame, frame_id), timeout=0.1)
            frame_id += 1
        except:
            pass

# ---------------- DETECT ----------------
def detect_thread():
    model = YOLO("best_ncnn_model")
    prev_time = time.time()

    while not stop_event.is_set():
        try:
            data = detect_queue.get(timeout=0.5)
        except Empty:
            continue

        if data.frame_id % DETECT_EVERY_N == 0:
            results = model(data.frame, classes=[0], conf=0.8, verbose=False)
            data.person_detected = len(results[0].boxes) > 0


        try:
            main_queue.put(data, timeout=0.1)
        except:
            pass

# ---------------- MAIN ------------------
def main_thread():
    last_state = None
    last_speak_time = 0

    # ----- FPS -----
    prev_time = time.time()
    fps = 0.0

    while not stop_event.is_set():
        try:
            data = main_queue.get(timeout=0.5)
        except Empty:
            continue

        # ----- TTS -----
        if data.person_detected and time.time() - last_speak_time > SPEAK_INTERVAL:
            speak_async("Person detected")
            send_frame_event(data.frame, "Person detected")
            last_speak_time = time.time()

        # ----- FPS CALC -----
        now = time.time()
        fps = 1 / (now - prev_time)
        prev_time = now


        # ----- VISUALIZE -----
        frame_vis = data.frame.copy()

        cv2.putText(
            frame_vis,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

        if data.person_detected:
            cv2.putText(
                frame_vis,
                "PERSON",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2
            )

        cv2.imshow("YOLO", frame_vis)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    cv2.destroyAllWindows()


# ---------------- MAIN ------------------
def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_SIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_SIZE[1])

    threads = [
        threading.Thread(target=camera_thread, args=(cap,), daemon=True),
        threading.Thread(target=detect_thread, daemon=True),
        threading.Thread(target=main_thread, daemon=True)
    ]

    for t in threads:
        t.start()

    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()

    cap.release()
    print("Program exited cleanly")

if __name__ == "__main__":
    main()
