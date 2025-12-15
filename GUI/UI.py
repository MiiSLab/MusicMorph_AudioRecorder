import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter

#System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

#App Frame
root = customtkinter.CTk()
root.geometry("1088x488")
root.title("Recording UI")

# Background image
bg_image = Image.open("./GUI_material/Background_1088_488.png")
bg_photo = customtkinter.CTkImage(light_image=bg_image, size=(1088, 488))

bg_label = customtkinter.CTkLabel(root, image=bg_photo, text="")
bg_label.place(relwidth=1, relheight=1)

# Add button with CTkImage
Add_img = Image.open("./GUI_material/add_76_30.png")
start_photo = customtkinter.CTkImage(light_image=Add_img, size=(76, 30))

# Define button actions
def start_recording():
    print("Recording started!")
    messagebox.showinfo("Recording", "Recording has started!")

# Create a transparent button
start_button = customtkinter.CTkButton(
    root,
    width=76,
    height=30,
    border_width=0,
    border_spacing=0,
    image=start_photo,
    text="",  # No text to only display the image
    fg_color="transparent",  # Make the button background transparent
    hover_color="#5e5e5e",  # Optional hover effect color
    command=start_recording,
)
start_button.place(x=200, y=400)

# Run App
root.mainloop()
