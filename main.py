import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
import sys

def crop_image_to_square(image_path, output_path):
    with Image.open(image_path) as img:
        min_side = min(img.size)
        left = (img.width - min_side) / 2
        top = (img.height - min_side) / 2
        right = (img.width + min_side) / 2
        bottom = (img.height + min_side) / 2

        img_cropped = img.crop((left, top, right, bottom))
        img_cropped.save(output_path)

def create_video(audio_path, image_path, output_path, progress_bar, status_label, window):
    try:
        FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
        if not os.path.exists(FFMPEG_PATH):
            status_label.config(text="❌ FFmpeg not found.")
            messagebox.showerror("Missing FFmpeg", "The file 'ffmpeg.exe' is missing.\nPlease place it next to the application.")
            return

        progress_bar.start()
        status_label.config(text="🔄 Creating video...")

        cropped_image = "cropped_temp.jpg"
        crop_image_to_square(image_path, cropped_image)

        command = [
            FFMPEG_PATH, "-loop", "1", "-i", cropped_image, "-i", audio_path,
            "-vf", "scale=1080:1080, pad=1920:1080:420:0:black",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
        ]

        subprocess.run(command, check=True)

        os.remove(cropped_image)
        status_label.config(text="✅ Video created successfully!")
        messagebox.showinfo("Success", f"Video has been successfully created:\n{output_path}")

    except Exception as e:
        status_label.config(text="❌ Error while creating video.")
        messagebox.showerror("Error", str(e))

    finally:
        progress_bar.stop()

def select_file(entry_field, filetypes):
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    entry_field.delete(0, tk.END)
    entry_field.insert(0, file_path)

def start_creation(audio_entry, image_entry, output_entry, progress_bar, status_label, window):
    audio = audio_entry.get()
    image = image_entry.get()
    output = output_entry.get()

    if not all([audio, image, output]):
        messagebox.showwarning("Missing fields", "Please fill in all the fields.")
        return

    thread = threading.Thread(target=create_video, args=(audio, image, output, progress_bar, status_label, window))
    thread.start()

# --- GUI Interface ---

window = tk.Tk()
window.title("Beats2Ytb - Type Beat Video Maker")
window.geometry("500x400")
icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icon.ico")
window.iconbitmap(default=icon_path)
window.resizable(False, False)

title = tk.Label(window, text="Beats2Ytb - Type Beat Video Maker", font=("Helvetica", 16, "bold"))
title.pack(pady=10)

# Audio file
tk.Label(window, text="Audio file (.mp3, .wav)").pack()
audio_entry = tk.Entry(window, width=50)
audio_entry.pack(pady=2)
tk.Button(window, text="Browse", command=lambda: select_file(audio_entry, [("Audio Files", "*.mp3;*.wav")])).pack()

# Image file
tk.Label(window, text="Image file (.jpg, .png)").pack()
image_entry = tk.Entry(window, width=50)
image_entry.pack(pady=2)
tk.Button(window, text="Browse", command=lambda: select_file(image_entry, [("Image Files", "*.jpg;*.png;*.jpeg")])).pack()

# Output video file
tk.Label(window, text="Output video name (.mp4)").pack()
output_entry = tk.Entry(window, width=50)
output_entry.pack(pady=2)
tk.Button(window, text="Save as", command=lambda: output_entry.insert(0, filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")]))).pack()

# Progress bar
progress_bar = ttk.Progressbar(window, mode='indeterminate', length=400)
progress_bar.pack(pady=20)

# Status
status_label = tk.Label(window, text="⏳ Waiting...", font=("Helvetica", 10, "italic"))
status_label.pack(pady=5)

# Start button
tk.Button(window, text="Create Video", font=("Helvetica", 12, "bold"), command=lambda: start_creation(audio_entry, image_entry, output_entry, progress_bar, status_label, window)).pack(pady=10)

window.mainloop()
