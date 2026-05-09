from ultralytics import YOLO
import cv2

# 1. Load a pre-trained 'Nano' model (Smallest/Fastest for CPU)
model = YOLO('yolov8n.pt') 

# 2. Run detection on your webcam
# '0' is usually the built-in laptop camera
results = model.predict(source="0", show=True, conf=0.5)

# The window will stay open until you press 'q' or stop the terminal