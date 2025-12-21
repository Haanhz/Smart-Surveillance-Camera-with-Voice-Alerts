from flask import Flask, request, jsonify, render_template
from datetime import datetime
import cv2
import time
import base64
import threading

app = Flask(__name__)

# ======= EVENT STORAGE =======
events = []
latest_frame = None  # store the latest YOLO frame


# ======= CAMERA CONFIG =======
VIDEO_SOURCE = 0  # 0 cho webcam máy tính, hoặc link stream từ Pi
cap = cv2.VideoCapture(VIDEO_SOURCE)
cap_lock = threading.Lock()

@app.route('/')
def index():
    return "Server is running. Use the Expo App to connect."

# Nhận sự kiện từ YOLO (ví dụ từ Raspberry Pi)
# Nhận sự kiện từ YOLO (ví dụ từ Raspberry Pi)
@app.route('/event', methods=['POST'])
def receive_event():
    data = request.get_json()
    event_text = data.get("event", "Unknown")
    ts = data.get("timestamp", time.time())
    frame_b64 = data.get("frame", "")  # <-- nhận frame từ YOLO nếu có

    timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    formatted = f"{timestamp} - {event_text}"
    events.append(formatted)

    # Lưu frame nếu có
    if frame_b64:
        global latest_frame
        latest_frame = base64.b64decode(frame_b64)

    print("[EVENT]", formatted)
    return jsonify({"status": "ok"}), 200


# Gửi cả Events và Ảnh mới nhất cho App
@app.route('/events', methods=['GET'])
def get_events():
    img_base64 = ""
    global latest_frame
    if latest_frame:
        img_base64 = base64.b64encode(latest_frame).decode('utf-8')

    return jsonify({
        "events": events,
        "image": img_base64
    })


if __name__ == '__main__':
    # Chạy trên 0.0.0.0 để các thiết bị trong Wi-Fi có thể truy cập
    app.run(host="192.168.1.168", port=5000, debug=False, threaded=True)
