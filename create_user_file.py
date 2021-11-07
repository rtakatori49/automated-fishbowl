import json
import os
import tkinter

from PIL import Image, ImageTk

# Load json
def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def create_user():
    user_dict = {
        "first_name": "",
        "last_name": "",
        "email": "",
        "group_name": "",
        "room_name": "",
        "selected_time": ""
    }


class UI:
    def __init__(self):
        self.icon_windows = "resources/fish.ico"
        self.geometry = "450x250"
        self.title = "Create User Profile"
        self.grids = {
            "page_name": "Please enter your information:",
            "first_name": "First Name:",
            "last_name": "Last Name:",
            "email": "Cal Poly Email:",
            "group_name": "Group Name:",
            "room_number": "Room Number:",
            "time": "Reservation Time:"
        }
        self.entries = [
            "First Name:",
            "Last Name:",
            "Cal Poly Email:",
            "Group Name:"
        ]
        self.dropdowns = [
            "Room Number:",
            "Reservation Time:"
        ]
        self.time_list = [
            "8:00 AM ~ 10:00 AM",
            "11:00 AM ~ 1:00 PM",
            "2:00 PM ~ 4:00 PM",
            "5:00 PM ~ 7:00 PM",
            "8:00 PM ~ 10:00 PM"
        ]

def create_grid(root, name, row, column=0, columnspan=1):
    grid_label = tkinter.Label(root, text=name)
    grid_label.grid(row=row,
                    column=column,
                    columnspan=columnspan)

def create_entry(root, row, column_entry=1, width=20):
    entry = tkinter.Entry(root, width=width)
    entry.grid(row=row, column=column_entry)
    return entry

def create_dropdown(root, variable_list, row, column_entry):
    variable = tkinter.StringVar(root)
    variable.set(variable_list[0])
    option_menu = tkinter.OptionMenu(root, variable, *variable_list)
    option_menu.grid(row=row, column=column_entry)
    return variable


def create_ui(ui):
    # Create UI
    root = tkinter.Tk()
    root.wm_iconbitmap(ui.icon_windows) # icon
    root.geometry(ui.geometry) # page size
    root.title(ui.title) # title
    for idx, name in enumerate(ui.grids):
        if idx == 0:
            create_grid(root, ui.grids[name], idx, columnspan=2)
        else:
            create_grid(root, ui.grids[name], idx)
<<<<<<< HEAD
        if ui.grids[name] in ui.entries:
=======
        if name in ui.entries:
>>>>>>> febfae0c0b126bf6cafbf87b64d563ed8576ab96
            create_entry(root, idx)
        if ui.grids[name] in ui.dropdowns:
            create_dropdown(root, idx)
    root.mainloop()
    user_dict = {
        "first_name": "",
        "last_name": "",
        "email": "",
        "group_name": "",
        "room_name": "",
        "selected_time": ""
    }
    return user_dict

def main():
    ui = UI()
    create_ui(ui)

if __name__ == "__main__":
    main()