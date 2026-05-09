# Titan Vision: Real-Time Spatial Intelligence & Geofencing

Titan Vision is a Computer Vision (CV) security framework designed to run high-speed inference on edge hardware (CPU-only). It implements a custom Sentry-Core HUD to monitor restricted zones using mathematical geofencing.

## Key Features
*   **Real-Time Inference:** Optimized for AMD Ryzen architectures using YOLOv8n.
*   **Geofencing:** Implements `pointPolygonTest` to trigger alerts based on centroid spatial location rather than simple detection.
*   **Automated Auditing:** Local evidence capture system with built-in cooldown logic to prevent disk overflow.
*   **Custom HUD:** Developed using an event-driven GUI architecture to bridge AI models with human operators.

## Technical Stack
*   **Model:** Ultralytics YOLOv8 (Nano)
*   **Graphics/UI:** OpenCV, CustomTkinter, Pillow
*   **Hardware:** Optimized for CPU-based execution[cite: 1].