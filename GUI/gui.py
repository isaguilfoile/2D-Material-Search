import tkinter as tk
from tkinter import ttk
import cv2
import threading
import time
import os
import subprocess
from PIL import Image, ImageTk

# Define color scheme
MAROON = "#800000"  # Dark maroon
GOLD = "#FFD700"    # Gold
LIGHT_MAROON = "#A52A2A"  # Lighter maroon for backgrounds
WHITE = "#FFFFFF"   # White for text

class CameraFeed:
    def __init__(self, label):
        self.label = label
        self.stop_event = threading.Event()
        self.cap = None
        self.thread = None
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.color = (255, 215, 0)  # Gold color for text (BGR format)
        self.thickness = 1

    def start(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Reduced from 3840
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Reduced from 2160
        self.thread = threading.Thread(target=self.update)
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                # Add position overlay
                pos_text = "X: 0.000 mm | Y: 0.000 mm"  # Placeholder for now
                cv2.putText(frame, pos_text, (10, 30), self.font, self.font_scale, 
                          self.color, self.thickness, cv2.LINE_AA)
                
                # Resize frame to fit in the GUI
                frame = cv2.resize(frame, (480, 360))  # Reduced from 640x480
                # Convert to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                # Update label
                self.label.config(image=photo)
                self.label.image = photo
            time.sleep(0.03)  # ~30 FPS

    def stop(self):
        self.stop_event.set()
        if self.cap is not None:
            self.cap.release()
        if self.thread is not None:
            self.thread.join()

def start_motormover():
    # Start MotorMover.py in a separate process
    global motormover_process
    motormover_process = subprocess.Popen(["python", "2D-Material-Search/MotorMover/MotorMover.py"])

def update_progress():
    # Path to the images folder
    images_dir = "2D-Material-Search/MotorMover/images/raw"
    
    # Count the number of image files
    image_count = len([f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
    
    # Update progress bar and label
    progress_bar['value'] = (image_count / 900) * 100
    progress_label.config(text=f"Progress: {image_count}/900 images", fg=GOLD)
    
    # Schedule next update if not at max
    if image_count < 900:
        root.after(1000, update_progress)  # Check every second

def on_start():
    start_button.config(text="Kill", command=on_kill, bg="red", fg=GOLD)
    label.config(text="Scanning!", font=("Times New Roman", 14, "bold"), fg=GOLD)
    camera_feed.start()
    start_motormover()  # Start the MotorMover process
    update_progress()  # Start progress monitoring

def on_kill():
    # Terminate the MotorMover process
    global motormover_process
    if 'motormover_process' in globals():
        motormover_process.terminate()
    camera_feed.stop()
    root.destroy()
    os._exit(0)  # Force terminate the program

def on_restart():
    camera_feed.stop()
    start_button.config(text="Start", command=on_start, bg=MAROON, fg=GOLD)
    label.config(text="Restarted, press start to begin with new measurements!", fg=GOLD)
    progress_bar['value'] = 0
    progress_label.config(text="Progress: 0/900 images", fg=GOLD)

root = tk.Tk()
root.title("2D Material Search")
root.geometry("800x700")  # Reduced window size
root.configure(bg=LIGHT_MAROON)

# Configure ttk style
style = ttk.Style()
style.configure("Maroon.Horizontal.TProgressbar", 
                troughcolor=LIGHT_MAROON,
                background=GOLD,
                bordercolor=MAROON)

# Create main container
main_container = tk.Frame(root, bg=LIGHT_MAROON)
main_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

# Logo at the top
logo_image = Image.open("2D-Material-Search/GUI/University-of-Minnesota-Logo.png")
logo_image = logo_image.resize((300, 150), Image.Resampling.LANCZOS)  # Increased from 250x125
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(main_container, image=logo_photo, bg=LIGHT_MAROON)
logo_label.image = logo_photo
logo_label.pack(pady=(0, 10))

# Status label
label = tk.Label(main_container, text="Press Start", font=("Times New Roman", 14), 
                bg=LIGHT_MAROON, fg=GOLD)
label.pack(pady=(0, 20))

# Camera feed frame
camera_frame = tk.Frame(main_container, bg=LIGHT_MAROON)
camera_frame.pack(pady=(0, 20))
camera_label = tk.Label(camera_frame, bg=LIGHT_MAROON)
camera_label.pack()
camera_feed = CameraFeed(camera_label)

# Progress section
progress_frame = tk.Frame(main_container, bg=LIGHT_MAROON)
progress_frame.pack(pady=(0, 10))  # Reduced padding

progress_label = tk.Label(progress_frame, text="Progress: 0/900 images", 
                         font=("Times New Roman", 12), bg=LIGHT_MAROON, fg=GOLD)
progress_label.pack()

progress_bar = ttk.Progressbar(progress_frame, length=500, mode='determinate',  # Reduced length
                             style="Maroon.Horizontal.TProgressbar")
progress_bar.pack(pady=5)  # Reduced padding

# Start/Kill button at the bottom
start_button = tk.Button(main_container, text="Start", command=on_start, 
                        font=("Times New Roman", 24), width=8, height=1,  # Reduced size
                        bg=MAROON, fg=GOLD, activebackground=GOLD,
                        activeforeground=MAROON)
start_button.pack(pady=(0, 10))  # Reduced padding

def on_closing():
    camera_feed.stop()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
