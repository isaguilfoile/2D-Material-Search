import tkinter as tk
from tkinter import ttk
import cv2
import threading
import time
import os
import sys
from PIL import Image, ImageTk

MotorMover_path = os.path.abspath("MotorMover/")
sys.path.insert(0, MotorMover_path)
from MotorMover import motor_move, snake_positions, offset_locations
from ImageCapture import DirectShowCam, find_available_cameras
from ConexCC import ConexCC

# Define color scheme
MAROON = "#800000"  # Dark maroon
GOLD = "#FFD700"    # Gold
LIGHT_MAROON = "#A52A2A"  # Lighter maroon for backgrounds
WHITE = "#FFFFFF"   # White for text

offsets= [0, 0]
major_locs = []
imagectr = 0
locals_idx = 0
position = [-1, 0, "right"]

# Initialize motor controllers
ConexCC.dump_possible_states()
conex_X = ConexCC(com_port='com5', velocity=0.5, dev=1)
conex_Y = ConexCC(com_port='com6', velocity=0.5, dev=1)

if conex_X.wait_for_ready(timeout=60) and conex_Y.wait_for_ready(timeout=60):
    conex_X.move_absolute(11.5)
    conex_Y.move_absolute(11.5)

class CameraDisplay:
    def __init__(self, label, camera):
        self.label = label
        self.camera = camera
        self.stop_event = threading.Event()
        self.thread = None
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.color = (255, 215, 0)  # Gold color for text (BGR format)
        self.thickness = 1

    def start(self):
        self.thread = threading.Thread(target=self.update)
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while not self.stop_event.is_set():
            try:
                frame = self.camera.get_frame()
                
                # Add position overlay
                pos_text = f"X: {conex_X.cur_pos:.3f} mm | Y: {conex_Y.cur_pos:.3f} mm"
                cv2.putText(frame, pos_text, (10, 30), self.font, self.font_scale, 
                          self.color, self.thickness, cv2.LINE_AA)
                
                # Resize frame to fit in the GUI - now 1.2x larger
                frame = cv2.resize(frame, (960, 720))  # 1.2x larger (800*1.2, 600*1.2)
                # Convert to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                # Update label
                self.label.config(image=photo)
                self.label.image = photo
            except Exception as e:
                print(f"Error updating camera display: {e}")
            time.sleep(0.03)  # ~30 FPS

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join()

def update_progress():
    global imagectr
    global locals_idx
    # Path to the images folder
    images_dir = "images/raw"
    
    # Count the number of image files
    image_count = len([f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
    if image_count != imagectr:
        imagectr = image_count - 1
    pos_text = f"X: {conex_X.cur_pos:.3f} mm | Y: {conex_Y.cur_pos:.3f} mm | Location {position[0]}{position[1]}"
    label.config(text=pos_text, font=("Times New Roman", 14, "bold"), fg=GOLD)
    # Update progress bar and label
    progress_bar['value'] = (image_count / 900) * 100
    progress_label.config(text=f"Progress: {image_count}/900 images", fg=GOLD)
    
    # Schedule next update if not at max
    if image_count < 900:
        root.after(1000, update_progress)  # Check every second

def on_start():
    start_button.config(text="End Fine Tuning", command=on_end_fine_tuning, bg=GOLD, fg=MAROON, width=14)
    label.config(text="Fine Tuning Mode", font=("Times New Roman", 14, "bold"), fg=GOLD)
    camera_display.start()

def check_motor_status():
    if not motor_thread.is_alive():
        # Motor movement has completed, return to fine-tuning state
        start_button.config(text="End Fine Tuning", command=re_end_fine_tune, bg=GOLD, fg=MAROON, width=14)
        label.config(text="Moving to new location", font=("Times New Roman", 14, "bold"), fg=GOLD)
        time.sleep(1)
        conex_X.move_absolute(major_locs[locals_idx][0])
        conex_Y.move_absolute(major_locs[locals_idx][1])
    else:
        # Check again in 1 second
        root.after(1000, check_motor_status)

def re_end_fine_tune():
    conex_X.read_cur_pos()
    conex_Y.read_cur_pos()
    global motor_thread
    global locals_idx
    global offsets
    global imagectr
    start_button.config(text="Kill", command=on_kill, bg="red", fg=GOLD, width=8)
    get_pos()
    pos_text = f"X: {conex_X.cur_pos:.3f} mm | Y: {conex_Y.cur_pos:.3f} mm | Location {position[0]}{position[1]}"
    label.config(text=pos_text, font=("Times New Roman", 14, "bold"), fg=GOLD)
    # Start motor movement in a separate thread
    offsetx = conex_X.cur_pos - major_locs[locals_idx][0]
    offsety = conex_Y.cur_pos - major_locs[locals_idx][1]
    offset_locations(offsetx, offsety, major_locs, locals_idx)
    locations = snake_positions(major_locs[locals_idx][0], major_locs[locals_idx][0] - 0.64, major_locs[locals_idx][1], major_locs[locals_idx][1] - 0.64, 0.16, 5)
    motor_thread = threading.Thread(target=motor_move, args=(conex_X, conex_Y, locations, imagectr, camera,))
    motor_thread.daemon = True
    motor_thread.start()
    locals_idx += 1
    offsets = [0,0]
    update_progress()  # Start progress monitoring
    # Start checking motor status
    check_motor_status()


def get_pos():
    global position
    if(position[2] == "right"):
        if(position[0] == 5):
            position[1] += 1
            position[2] == "left"
        else:
            position[0] += 1
    else:
        if(position[0] == 0):
            position[1] += 1
            position[2] == "right"
        else:
            position[0] -= 1

def on_end_fine_tuning():
    conex_X.read_cur_pos()
    conex_Y.read_cur_pos()
    global motor_thread
    global locals_idx
    global major_locs
    global offsets
    global imagectr
    start_button.config(text="Kill", command=on_kill, bg="red", fg=GOLD, width=8)
    get_pos()
    pos_text = f"X: {conex_X.cur_pos:.3f} mm | Y: {conex_Y.cur_pos:.3f} mm | Location {position[0]}{position[1]}"
    label.config(text=pos_text, font=("Times New Roman", 14, "bold"), fg=GOLD)
    endx = conex_X.cur_pos - 5.25
    endy = conex_Y.cur_pos - 5.25
    major_locs = snake_positions(conex_X.cur_pos, endx, conex_Y.cur_pos, endy, 1.05, 6)
    # Start motor movement in a separate thread
    print("out,", conex_X.cur_pos, conex_Y.cur_pos)
    locations = snake_positions(major_locs[locals_idx][0], major_locs[locals_idx][0] - 0.64, major_locs[locals_idx][1], major_locs[locals_idx][1] - 0.64, 0.16, 5)
    motor_thread = threading.Thread(target=motor_move, args=(conex_X, conex_Y, locations, imagectr, camera,))
    motor_thread.daemon = True
    motor_thread.start()
    locals_idx += 1
    offsets = [0, 0]
    update_progress()  # Start progress monitoring
    # Start checking motor status
    check_motor_status()

def on_kill():
    # Terminate the MotorMover process
    camera_display.stop()
    camera.close()
    conex_X.close()
    conex_Y.close()
    root.destroy()
    os._exit(0)  # Force terminate the program

def on_fine_tune(direction):
    step_size = 0.01  # mm
    global offsets
    if direction == "up":
        conex_Y.move_relative(-step_size)
        offsets[1] += -step_size
    elif direction == "down":
        conex_Y.move_relative(step_size)
        offsets[1] += step_size
    elif direction == "left":
        conex_X.move_relative(step_size)
        offsets[0] += step_size
    elif direction == "right":
        conex_X.move_relative(-step_size)
        offsets[0] += -step_size
    # Update the camera display immediately after movement
    try:
        frame = camera.get_frame()
        frame = cv2.resize(frame, (960, 720))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        camera_label.config(image=photo)
        camera_label.image = photo
    except Exception as e:
        print(f"Error updating camera display during fine-tuning: {e}")

root = tk.Tk()
root.title("2D Material Search")
root.geometry("1600x1000")  # Further increased window size
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

# Create left panel for controls
left_panel = tk.Frame(main_container, bg=LIGHT_MAROON, width=400)  # Further increased width for left panel
left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
left_panel.pack_propagate(False)  # Prevent panel from shrinking

# Create right panel for camera feed
right_panel = tk.Frame(main_container, bg=LIGHT_MAROON)
right_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Logo at the top of left panel
logo_image = Image.open("GUI/University-of-Minnesota-Logo.png")
logo_image = logo_image.resize((350, 175), Image.Resampling.LANCZOS)  # Larger logo
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(left_panel, image=logo_photo, bg=LIGHT_MAROON)
logo_label.image = logo_photo
logo_label.pack(pady=(0, 20))

# Status label
label = tk.Label(left_panel, text="Press Start", font=("Times New Roman", 14), 
                bg=LIGHT_MAROON, fg=GOLD, width=35)  # Further increased width
label.pack(pady=(0, 20))

# Camera feed frame in right panel
camera_frame = tk.Frame(right_panel, bg=LIGHT_MAROON)
camera_frame.pack(expand=True, fill=tk.BOTH)
camera_label = tk.Label(camera_frame, bg=LIGHT_MAROON)
camera_label.pack(expand=True, fill=tk.BOTH)

# Initialize camera
camera = DirectShowCam(camera_index=1, directory="images/raw")
camera_display = CameraDisplay(camera_label, camera)

# Fine-tuning controls in left panel
fine_tune_frame = tk.Frame(left_panel, bg=LIGHT_MAROON)
fine_tune_frame.pack(pady=(0, 20))

# Fine-tuning buttons
up_button = tk.Button(fine_tune_frame, text="↑", command=lambda: on_fine_tune("up"),
                     font=("Times New Roman", 12), width=3, height=1,
                     bg=MAROON, fg=GOLD, activebackground=GOLD,
                     activeforeground=MAROON)
up_button.grid(row=0, column=1, padx=5, pady=5)

left_button = tk.Button(fine_tune_frame, text="←", command=lambda: on_fine_tune("left"),
                       font=("Times New Roman", 12), width=3, height=1,
                       bg=MAROON, fg=GOLD, activebackground=GOLD,
                       activeforeground=MAROON)
left_button.grid(row=1, column=0, padx=5, pady=5)

right_button = tk.Button(fine_tune_frame, text="→", command=lambda: on_fine_tune("right"),
                        font=("Times New Roman", 12), width=3, height=1,
                        bg=MAROON, fg=GOLD, activebackground=GOLD,
                        activeforeground=MAROON)
right_button.grid(row=1, column=2, padx=5, pady=5)

down_button = tk.Button(fine_tune_frame, text="↓", command=lambda: on_fine_tune("down"),
                       font=("Times New Roman", 12), width=3, height=1,
                       bg=MAROON, fg=GOLD, activebackground=GOLD,
                       activeforeground=MAROON)
down_button.grid(row=2, column=1, padx=5, pady=5)

# Progress section in left panel
progress_frame = tk.Frame(left_panel, bg=LIGHT_MAROON)
progress_frame.pack(pady=(0, 20))

progress_label = tk.Label(progress_frame, text="Progress: 0/900 images", 
                         font=("Times New Roman", 12), bg=LIGHT_MAROON, fg=GOLD)
progress_label.pack()

progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate',
                             style="Maroon.Horizontal.TProgressbar")
progress_bar.pack(pady=5)

# Start/Kill button at the bottom of left panel
start_button = tk.Button(left_panel, text="Start", command=on_start, 
                        font=("Times New Roman", 24), width=8, height=1,
                        bg=MAROON, fg=GOLD, activebackground=GOLD,
                        activeforeground=MAROON)
start_button.pack(pady=(0, 10))

def on_closing():
    camera_display.stop()
    camera.close()
    conex_X.close()
    conex_Y.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
