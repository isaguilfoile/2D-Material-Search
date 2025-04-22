import tkinter as tk
import subprocess
from PIL import Image, ImageTk

def on_start():
    start_button.config(text="Re-Start", command=on_restart)
    step_size = stepentry1.get() # TODO: send to motor mover 
    speed_val = speedentry2.get()
    range_val = rangeentry3.get()
    if not is_numeric(step_size) or not is_numeric(speed_val) or not is_numeric(range_val):
        on_error()
        return
    label.config(text="Scanning!")
    step.config(text="Step Size: " + step_size + " micrometers")
    range.config(text="Range: " + range_val + " x" + range_val)
    speed.config(text="Speed: " + speed_val + " um/s")

    #TODO: call processes
    # subprocess.run(["matlab", "-batch", "name"])
    # img = Image.open("goat.webp")  #
    # img = img.resize((200, 200))  # Resize as needed
    # img_tk = ImageTk.PhotoImage(img)
    # image_label.config(image=img_tk)
    # image_label.image = img_tk

def on_error():
    start_button.config(text="Start", command=on_start)
    step.config(text="Input New Step Size:")
    speed.config(text="Input New Speed:")
    range.config(text="Input New Range:")
    label.config(text="❌ Error: All inputs must be numeric ❌")

def on_restart():
    # TODO: reset motors to "home" position on restart
    start_button.config(text="Start", command=on_start)
    step.config(text="Input New Step Size:")
    speed.config(text="Input New Speed:")
    range.config(text="Input New Range:")
    label.config(text="Restarted, press start to begin with new measurements!")

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

root = tk.Tk()
root.title("2D Material Search")
root.geometry("700x700")

label = tk.Label(root, text="Press Start", font=("Times New Roman", 14))
label.pack(pady=20)

# input for step size
step = tk.Label(root, text="Step Size (um):", font=("Times New Roman", 12))
step.pack()
stepentry1 = tk.Entry(root, font=("Times New Roman", 14), width=30)
stepentry1.pack(pady=10)
stepentry1.insert(0, " ")

# input for speed
speed = tk.Label(root, text="Speed (um/s):", font=("Times New Roman", 12))
speed.pack()
speedentry2 = tk.Entry(root, font=("Times New Roman", 14), width=30)
speedentry2.pack(pady=10)
speedentry2.insert(0, " ")

# input for range
range = tk.Label(root, text="Range (x by x): ", font=("Times New Roman", 12))
range.pack()
rangeentry3 = tk.Entry(root, font=("Times New Roman", 14), width=30)
rangeentry3.pack(pady=10)
rangeentry3.insert(0, " ")

image_label = tk.Label(root) 
image_label.pack()

start_button = tk.Button(root, text="Start", command=on_start, font=("Times New Roman", 30), width=10, height=2,bg="green", fg="white")
start_button.pack()


root.mainloop()
