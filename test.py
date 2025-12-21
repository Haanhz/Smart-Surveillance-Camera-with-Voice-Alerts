import cv2
from ultralytics import YOLO
import subprocess
import requests
import time


# ---- Khởi tạo YOLOv8 ----
cap = cv2.VideoCapture(0)
model = YOLO('best_ncnn_model')


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    results = model(frame)
    result = results[0]
    print(result)
    frame_vis = result.plot()
    cv2.imshow('YOLO Detection', frame_vis)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
