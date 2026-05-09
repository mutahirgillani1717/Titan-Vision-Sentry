import cv2
from ultralytics import YOLO

# 1. Load the model
model = YOLO('yolov8n.pt')

# 2. Hook into the webcam directly using OpenCV
cap = cv2.VideoCapture(0)
print("Starting Titan Security Camera... Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 3. Run inference quietly (without the default YOLO popup)
    results = model(frame, stream=True, verbose=False)
    
    # 4. Intercept the AI's "Brain"
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # YOLO knows 80 objects. Class 0 is 'Person'.
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            # If it's a person AND the AI is at least 60% sure...
            if class_id == 0 and confidence > 0.60:
                
                # Get the mathematical coordinates of the bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Draw a thick RED box (BGR format in OpenCV)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                
                # Add custom UI text
                alert_text = f"INTRUDER DETECTED: {confidence*100:.1f}%"
                cv2.putText(frame, alert_text, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Draw a red warning border around the entire camera feed
                cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 10)

    # 5. Display our custom engineered frame
    cv2.imshow("Titan Vision - Secure Mode", frame)

    # Quit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up hardware resources
cap.release()
cv2.destroyAllWindows()