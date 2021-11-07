# Create User File for Automated Fishbowl Reservation
# Ryo Takatori
# 2021-11-07

# Modules
import json
import os
import sys
import tkinter

from tkinter import messagebox
from PIL import Image, ImageTk

# Load json
def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

# Dump json
def dump_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=6)

# UI class
class UI:
    def __init__(self):
        self.icon_windows = "resources/fish.ico"
        self.icon_linux = "resources/fish.xbm"
        self.image = "resources/fishbowl.gif"
        self.geometry = "450x250"
        self.title = "Create User Profile"
        self.grids = [
            "Please enter your information:",
            "First Name:",
            "Last Name:",
            "Cal Poly Email:",
            "Group Name:",
            "Room Number:",
            "Reservation Time:"
        ]
        self.entries = [
            "First Name:",
            "Last Name:",
            "Cal Poly Email:",
            "Group Name:"
        ]
        self.dropdowns = {
            "Room Number:": [x for x in load_json("time_element.json")],
            "Reservation Time:": [x for x in load_json("reserve_time.json")]
        }

# Create grid
def create_grid(root, name, row, column=0, columnspan=1):
    grid_label = tkinter.Label(root, text=name)
    grid_label.grid(row=row,
                    column=column,
                    columnspan=columnspan)

# Create entry
def create_entry(root, row, column_entry=1, width=20):
    entry = tkinter.Entry(root, width=width)
    entry.grid(row=row, column=column_entry)
    return entry

# Create dropdown
def create_dropdown(root, variable_list, row, column_entry=1):
    variable = tkinter.StringVar(root)
    variable.set(variable_list[0])
    option_menu = tkinter.OptionMenu(root, variable, *variable_list)
    option_menu.grid(row=row, column=column_entry)
    return variable

# Create UI
def create_ui():
    ui = UI()
    root = tkinter.Tk()
    root.wm_iconbitmap(ui.icon_windows) # icon
    root.geometry(ui.geometry) # page size
    root.title(ui.title) # title
    entry_list = []
    for idx, name in enumerate(ui.grids):
        if idx == 0:
            create_grid(root, name, idx, columnspan=2)
        else:
            create_grid(root, name, idx)
        if name in ui.entries:
            entry_list.append(create_entry(root, idx))
        if name in ui.dropdowns:
            entry_list.append(create_dropdown(root, ui.dropdowns[name], idx))
    # Image
    image = Image.open(ui.image)
    photo = ImageTk.PhotoImage(image)
    photo_label = tkinter.Label(image=photo)
    photo_label.image = photo # this line need to prevent gc
    photo_label.grid(row=0, column=2, columnspan=7, rowspan=7)
    # Submission
    def my_click():
        user_dict = {
            "first_name": entry_list[0].get(),
            "last_name": entry_list[1].get(),
            "email": entry_list[2].get(),
            "group_name": entry_list[3].get(),
            "room_name": entry_list[4].get(),
            "selected_time": entry_list[5].get()
        }
        dump_json(user_dict, "user.json")
        root.quit()
    my_button = tkinter.Button(root, text="Submit", command=my_click)
    my_button.grid(row=7, column=1)
    root.mainloop()
    messagebox.showinfo("Completed!",
        "Initial information applied. "\
        "Please configure Task Scheduler to automate reservation.")
    sys.exit(0)

def main():
    if os.path.isfile("user.json"):
        messagebox.showinfo("Completed!",
            "User already configured. "\
            "Please configure Task Scheduler to automate reservation.")
        sys.exit(0)
    else:
        create_ui()

if __name__ == "__main__":
    main()