import cv2
import numpy as np
from ultralytics import YOLO
import os
from datetime import datetime
import time

# 1. Setup Evidence Directory
if not os.path.exists('intruders'):
    os.makedirs('intruders')
    print("Created 'intruders' directory for evidence logs.")

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)

# 2. Define the Restricted Zone (Geofencing)
# These coordinates map to a rectangle in the center of a standard webcam feed.
zone_points = np.array([[150, 100], [450, 100], [450, 400], [150, 400]], np.int32)
zone_polygon = zone_points.reshape((-1, 1, 2))

# 3. Prevent hard-drive spam with a cooldown timer
last_save_time = 0
cooldown_seconds = 3 

print("System Armed. Press 'q' to disarm and exit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Draw the safe zone in Blue
    cv2.polylines(frame, [zone_polygon], isClosed=True, color=(255, 0, 0), thickness=2)
    cv2.putText(frame, "RESTRICTED ZONE", (150, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    results = model(frame, stream=True, verbose=False)

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id == 0 and confidence > 0.60:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Calculate the "Centroid" (the dead center of the person)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # Draw a green dot tracking their center
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                # 4. SPATIAL LOGIC: Is the centroid inside the polygon?
                # cv2.pointPolygonTest returns > 0 if inside, 0 if on the line, < 0 if outside
                inside = cv2.pointPolygonTest(zone_polygon, (cx, cy), False)

                if inside >= 0: 
                    # BREACH PROTOCOL
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(frame, "BREACH!", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                    
                    # Flash the geofence Red
                    cv2.polylines(frame, [zone_polygon], isClosed=True, color=(0, 0, 255), thickness=4)

                    # 5. AUDIT LOGGING: Save the evidence
                    current_time = time.time()
                    if current_time - last_save_time > cooldown_seconds:
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        filename = f"intruders/breach_{timestamp}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"[!] EVIDENCE CAPTURED: {filename}")
                        last_save_time = current_time

    cv2.imshow("Titan Vision - Security Matrix", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()