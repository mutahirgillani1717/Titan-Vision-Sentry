# Titan Vision: Sentry-Core Spatial Intelligence

Titan Vision is a high-performance Computer Vision (CV) framework engineered to monitor restricted environments. It bridges the gap between raw Object Detection and active Security Auditing by implementing real-time spatial geofencing.

## 🛡️ Core Engineering Features
*   **Mathematical Geofencing:** Utilizes the `pointPolygonTest` algorithm to track the centroid (center mass) of detected targets against user-defined restricted zones.
*   **Sentry-Core HUD:** A custom-built Desktop interface designed with `CustomTkinter` for real-time AI parameter tuning (Confidence & Sensitivity).
*   **Evidence Logging:** Automated file-system handler that captures timestamped security breaches with a built-in temporal cooldown to prevent disk saturation.
*   **Edge Optimization:** Optimized for high-frequency inference on AMD Ryzen CPU architectures via YOLOv8n (Nano).

## 🛠️ Technical Stack
*   **Vision Engine:** Ultralytics YOLOv8
*   **Image Processing:** OpenCV (Open Source Computer Vision Library)
*   **UI Architecture:** CustomTkinter & Pillow (PIL)
*   **Core Math:** NumPy (Vectorized coordinate operations)[cite: 1]

## 🚀 Execution
1. Create environment: `conda create --name titan_vision python=3.10`[cite: 1]
2. Install dependencies: `pip install ultralytics opencv-python customtkinter pillow`[cite: 1]
3. Initialize the HUD: `python titan_dashboard.py`[cite: 1]