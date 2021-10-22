import json
import os
import tkinter

from PIL import Image, ImageTk

from automated_fishbowl import load_json

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
        d = load_json("ui_config.json")
        self.icon = d["icon"]
        self.geometry = d["geometry"]
        self.title = d["title"]
        self.grids = d["grids"]
        self.entries = d["entries"]
        self.dropdowns = d["dropdowns"]

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
    root.wm_iconbitmap(ui.icon) # icon
    root.geometry(ui.geometry) # page size
    root.title(ui.title) # title
    for idx, name in enumerate(ui.grids):
        if idx == 0:
            create_grid(root, name, idx, columnspan=2)
        else:
            create_grid(root, name, idx)
        if name in ui.entries:
            create_entry(root, idx)
        if name in ui.dropdowns:
            create_dropdown(root, idx,)
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