import tkinter as tk
import subprocess
from PIL import Image, ImageTk

def on_start():
    label.config(text="Scanning!")
    # subprocess.run(["matlab", "-batch", "name"])
    img = Image.open("goat.webp")  #
    img = img.resize((200, 200))  # Resize as needed
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk

root = tk.Tk()
root.title("2D Material Search")
root.geometry("700x700")

label = tk.Label(root, text="Press Start", font=("Times New Roman", 14))
label.pack(pady=20)


image_label = tk.Label(root) 
image_label.pack()

start_button = tk.Button(root, text="Start", command=on_start, font=("Times New Roman", 30), width=10, height=2,bg="green", fg="white")
start_button.pack()


root.mainloop()
