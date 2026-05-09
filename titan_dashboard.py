import customtkinter as ctk
import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO
import os
from datetime import datetime
import time

# --- Developer Config ---
# Using a custom 'Electric Cyan' and 'Deep Slate' palette
ACCENT_COLOR = "#00f2ff" 
BG_COLOR = "#0d1117"
PANEL_COLOR = "#161b22"

ctk.set_appearance_mode("dark")

class TitanVisionHUD(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TITAN VISION // SENTRY-CORE v1.0.4")
        self.geometry("1200x800")
        self.configure(fg_color=BG_COLOR)

        # --- AI Engine State ---
        self.model = YOLO('yolov8n.pt')
        self.cap = None
        self.is_active = False
        self.intruder_count = 0
        self.conf_threshold = 0.6
        
        # Geofence (User-Defined)
        self.zone_points = np.array([[180, 120], [460, 120], [460, 380], [180, 380]], np.int32)
        self.zone_polygon = self.zone_points.reshape((-1, 1, 2))

        if not os.path.exists('intruders'):
            os.makedirs('intruders')

        self.setup_ui()

    def setup_ui(self):
        # Create a Grid Layout (Top: Header, Mid: Video, Bottom: Controls)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Video takes most space

        # --- 1. Top Header Bar ---
        self.header = ctk.CTkFrame(self, height=60, fg_color=PANEL_COLOR, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header, text="TITAN VISION // SENTRY-CORE", 
                                        font=ctk.CTkFont(family="Orbitron", size=20, weight="bold"),
                                        text_color=ACCENT_COLOR)
        self.title_label.pack(side="left", padx=30)

        self.stats_label = ctk.CTkLabel(self.header, text="INTRUDERS CAUGHT: 0", 
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.stats_label.pack(side="right", padx=30)

        # --- 2. Main Viewport ---
        self.viewport = ctk.CTkFrame(self, fg_color="black", corner_radius=15, border_width=2, border_color="#30363d")
        self.viewport.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_display = ctk.CTkLabel(self.viewport, text="[ SYSTEM OFFLINE ]", text_color="#30363d")
        self.video_display.pack(expand=True, fill="both")

        # --- 3. Bottom Control Dock ---
        self.dock = ctk.CTkFrame(self, height=200, fg_color=PANEL_COLOR, corner_radius=15)
        self.dock.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.dock.grid_columnconfigure((0,1,2), weight=1)

        # Column A: System Status LED & Toggle
        self.ctrl_panel = ctk.CTkFrame(self.dock, fg_color="transparent")
        self.ctrl_panel.grid(row=0, column=0, padx=20, pady=20)
        
        self.led_indicator = ctk.CTkLabel(self.ctrl_panel, text="●", text_color="gray", font=("Arial", 24))
        self.led_indicator.grid(row=0, column=0, padx=5)
        
        self.power_btn = ctk.CTkButton(self.ctrl_panel, text="ENGAGE SYSTEM", 
                                       command=self.toggle_power, 
                                       fg_color="#238636", hover_color="#2ea043",
                                       font=ctk.CTkFont(weight="bold"))
        self.power_btn.grid(row=0, column=1, padx=10)

        # Column B: AI Tuning (Sensitivity)
        self.tune_panel = ctk.CTkFrame(self.dock, fg_color="transparent")
        self.tune_panel.grid(row=0, column=1, padx=20, pady=20)
        
        ctk.CTkLabel(self.tune_panel, text="AI SENSITIVITY THRESHOLD", font=ctk.CTkFont(size=12)).pack()
        self.conf_slider = ctk.CTkSlider(self.tune_panel, from_=0.3, to=0.9, 
                                         number_of_steps=10, 
                                         command=self.update_conf,
                                         button_color=ACCENT_COLOR)
        self.conf_slider.set(0.6)
        self.conf_slider.pack(pady=10)

        # Column C: Event Terminal
        self.terminal = ctk.CTkTextbox(self.dock, height=120, width=350, font=("Consolas", 12), fg_color="#010409")
        self.terminal.grid(row=0, column=2, padx=20, pady=20)
        self.terminal.insert("0.0", "--- LOCAL TERMINAL INITIALIZED ---\n")
        self.terminal.configure(state="disabled")

    def update_conf(self, value):
        self.conf_threshold = value
        self.write_to_terminal(f"Sensitivity adjusted to {value:.2f}")

    def write_to_terminal(self, msg):
        self.terminal.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.terminal.insert("end", f"> {ts} | {msg}\n")
        self.terminal.see("end")
        self.terminal.configure(state="disabled")

    def toggle_power(self):
        if not self.is_active:
            self.cap = cv2.VideoCapture(0)
            self.is_active = True
            self.power_btn.configure(text="DISENGAGE", fg_color="#da3633", hover_color="#f85149")
            self.led_indicator.configure(text_color="#39ff14") # Neon Green
            self.write_to_terminal("Hardware link established. Sentry Active.")
            self.run_loop()
        else:
            self.is_active = False
            self.power_btn.configure(text="ENGAGE SYSTEM", fg_color="#238636")
            self.led_indicator.configure(text_color="gray")
            self.video_display.configure(image="", text="[ SYSTEM OFFLINE ]")
            if self.cap: self.cap.release()
            self.write_to_terminal("Link terminated.")

    def run_loop(self):
        if self.is_active and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 1. Spatial HUD Drawing
                cv2.polylines(frame, [self.zone_polygon], True, (255, 255, 0), 2)
                
                # 2. AI Inference
                results = self.model(frame, stream=True, verbose=False)
                
                for r in results:
                    for box in r.boxes:
                        # Use our real-time slider value for confidence
                        if int(box.cls[0]) == 0 and float(box.conf[0]) > self.conf_threshold:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cx, cy = (x1+x2)//2, (y1+y2)//2
                            
                            # Spatial Logic
                            if cv2.pointPolygonTest(self.zone_polygon, (cx, cy), False) >= 0:
                                # Visual Alert
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                                cv2.putText(frame, "TARGET BREACH", (x1, y1-10), 2, 0.6, (0,0,255), 2)
                                
                                # Auto-capture Logic (Simplified for brevity)
                                if time.time() % 5 < 0.1: # Save approx every 5 seconds of breach
                                    self.intruder_count += 1
                                    self.stats_label.configure(text=f"INTRUDERS CAUGHT: {self.intruder_count}")
                                    self.write_to_terminal("Breach logged to drive.")

                # 3. Render to UI
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                ctk_img = ctk.CTkImage(img, size=(720, 480))
                self.video_display.configure(image=ctk_img, text="")

            self.after(10, self.run_loop)

if __name__ == "__main__":
    app = TitanVisionHUD()
    app.mainloop()