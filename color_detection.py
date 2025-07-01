import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Label, Listbox, Scrollbar, ttk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd

# === CONFIGURATION ===
csv_path = 'colors.csv'  # Must be in the same folder as this .py file
img_folder = 'images'    # Folder to store default and uploaded images
default_img_name = 'living_room.jpeg'
default_img_path = os.path.join(img_folder, default_img_name)

# === SETUP ===
# Create image folder if it doesn't exist
if not os.path.exists(img_folder):
    os.makedirs(img_folder)

# Load CSV color data
index = ['color', 'color_name', 'hex', 'R', 'G', 'B']
try:
    df = pd.read_csv(csv_path, names=index, header=None)
except FileNotFoundError:
    tk.Tk().withdraw()  # Hide main window
    messagebox.showerror("Error", f"CSV file '{csv_path}' not found.")
    exit()

# Check default image
if not os.path.exists(default_img_path):
    tk.Tk().withdraw()
    messagebox.showerror("Error", f"Default image '{default_img_path}' not found.\nAdd an image named '{default_img_name}' to the 'images' folder.")
    exit()

# === FUNCTIONS ===

# Find closest color
def get_color_name(R, G, B):
    min_dist = float('inf')
    cname, hex_value = "Unknown", "#000000"
    R, G, B = np.clip([R, G, B], 0, 255)
    for i in range(len(df)):
        csv_R, csv_G, csv_B = np.clip([int(df.loc[i, 'R']), int(df.loc[i, 'G']), int(df.loc[i, 'B'])], 0, 255)
        dist = np.sqrt((R - csv_R)**2 + (G - csv_G)**2 + (B - csv_B)**2)
        if dist < min_dist:
            min_dist = dist
            cname, hex_value = df.loc[i, 'color_name'], df.loc[i, 'hex']
    return cname, hex_value

# Load and resize image for display
def load_image(path, width, height):
    img = Image.open(path)
    img = img.resize((width, height))
    return ImageTk.PhotoImage(img)

# === GUI SETUP ===

root = tk.Tk()
root.title("Color Detector")
root.configure(bg="#2c3e50")
root.geometry("1024x700")
root.attributes("-fullscreen", False)
root.bind("<F11>", lambda e: root.attributes("-fullscreen", True))
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

image_width, image_height = 800, 500
uploaded_images = []

# Display default image
current_img_path = default_img_path
img_display = load_image(current_img_path, image_width, image_height)
img_label = Label(root, image=img_display, bg="#2c3e50")
img_label.pack(pady=10)

# Detect color on click
def detect_color(event):
    x, y = event.x, event.y
    if 0 <= x < image_width and 0 <= y < image_height:
        img_cv = cv2.imread(current_img_path)
        img_cv = cv2.resize(img_cv, (image_width, image_height))
        b, g, r = img_cv[y, x]
        color_name, hex_value = get_color_name(r, g, b)
        color_box.config(bg=hex_value)
        color_info.config(text=f"Color: {color_name}\nRGB: {r}, {g}, {b}\nHEX: {hex_value}")

img_label.bind("<Button-1>", detect_color)

# Upload image
def upload_image():
    global img_display, current_img_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if file_path:
        save_choice = messagebox.askyesno("Save Image", "Do you want to save this image permanently?")
        if save_choice:
            new_image_path = os.path.join(img_folder, os.path.basename(file_path))
            Image.open(file_path).save(new_image_path)
            stored_name = os.path.basename(file_path)
        else:
            stored_name = os.path.basename(file_path)
        uploaded_images.append(stored_name)
        img_display = load_image(file_path, image_width, image_height)
        img_label.config(image=img_display)
        current_img_path = file_path
        update_menu()

# Update right-side menu with image names
def update_menu():
    menu_list.delete(0, tk.END)
    for file in os.listdir(img_folder):
        if file.lower().endswith(('.jpg', '.png', '.jpeg')):
            menu_list.insert(tk.END, file)
    for image in uploaded_images:
        if image not in menu_list.get(0, tk.END):
            menu_list.insert(tk.END, image)

# Select image from the list
def select_image(event):
    global img_display, current_img_path
    selected_index = menu_list.curselection()
    if selected_index:
        image_name = menu_list.get(selected_index)
        img_path = os.path.join(img_folder, image_name)
        if os.path.exists(img_path):
            img_display = load_image(img_path, image_width, image_height)
            img_label.config(image=img_display)
            current_img_path = img_path

# Close app
def on_close():
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# === RIGHT MENU UI ===
menu_frame = tk.Frame(root, bg="#2c3e50")
menu_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=10)

scrollbar = Scrollbar(menu_frame, orient=tk.VERTICAL)
menu_list = Listbox(menu_frame, height=15, yscrollcommand=scrollbar.set, font=("Arial", 12), bg="#34495e", fg="white", selectbackground="#0078D7", selectforeground="white")
scrollbar.config(command=menu_list.yview)
menu_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

menu_list.bind("<Double-Button-1>", select_image)

# === COLOR INFO DISPLAY ===
color_box = tk.Label(root, bg="#000000", width=20, height=2)
color_box.pack(pady=5)

color_info = tk.Label(root, text="Click on the image to detect color", fg="white", bg="#2c3e50", font=("Arial", 14))
color_info.pack(pady=5)

upload_button = tk.Button(root, text="Upload Image", command=upload_image, bg="#0078D7", fg="white", padx=15, pady=8, font=("Arial", 12, "bold"))
upload_button.pack(side=tk.RIGHT, anchor="se", padx=20, pady=20)

# Load menu
update_menu()
root.mainloop()
