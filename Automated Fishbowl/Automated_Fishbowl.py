# Automated Fishbowl Reserver
# Ryo Takatori
# 04/06/2020
# Created to automate fishbowl reservation

# Libraries
from selenium import webdriver
import os.path
from datetime import datetime, timedelta
from time import sleep
from tkinter import *
from PIL import Image, ImageTk

# Create grid
class GridCreator:
    def __init__(self, root, name, row, column, columnspan):
        self.root = root
        self.name = name
        self.row = row
        self.column = column
        self.columnspan = columnspan
    def create_grid(self):
            Label(self.root, text=self.name).grid(row=self.row, column=self.column, columnspan=self.columnspan)

# Create entry
class EntryCreator(GridCreator):
    def __init__(self, root, name, row, column, columnspan, column_entry, width):
        super().__init__(root, name, row, column, columnspan)
        self.column_entry = column_entry
        self.width = width
    def create_entry(self):
        super().create_grid()
        entry = Entry(self.root, width=self.width)
        entry.grid(row=self.row, column=self.column_entry)
        return entry

# Create dropdown
class DropdownCreator(GridCreator):
    def __init__(self, root, name, row, column, columnspan, column_entry, variable_list):
        super().__init__(root, name, row, column, columnspan)
        self.column_entry = column_entry
        self.variable_list = variable_list
    def create_dropdown(self):
        super().create_grid()
        variable = StringVar(self.root)
        variable.set(self.variable_list[0])
        OptionMenu(self.root, variable, *self.variable_list).grid(row=self.row, column=self.column_entry)
        return variable

# User interface for initial information
room_number_list = ["216L",
                    "216N",
                    "216Q",
                    "216S"
]
time_list = ["8:00 AM ~ 10:00 AM",
             "11:00 AM ~ 1:00 PM",
             "2:00 PM ~ 4:00 PM",
             "5:00 PM ~ 7:00 PM",
             "8:00 PM ~ 10:00 PM",
]
file_exists = os.path.isfile("userinfo.txt")
if not file_exists:
    # Page settings
    root = Tk()
    root.wm_iconbitmap('fish.ico') # Icon
    root.geometry("450x250") # Size
    root.title("Automated Fishbowl Reserver") # Title
    grid_title = GridCreator(root,"Please enter your information:",0,0,2).create_grid() # Grid title
    first_name = EntryCreator(root,"First Name:",1,0,1,1,20).create_entry() # First name
    last_name = EntryCreator(root,"Last Name:",2,0,1,1,20).create_entry() # Last name
    email = EntryCreator(root,"Cal Poly Email:",3,0,1,1,20).create_entry() # Email
    group_name = EntryCreator(root,"Group Name:",4,0,1,1,20).create_entry() # Group name
    room_number = DropdownCreator(root,"Room Number:",5,0,1,1,room_number_list).create_dropdown() # Room number
    time = DropdownCreator(root,"Reservation Time:",6,0,1,1,time_list).create_dropdown() # Reservation time

    # Image
    image = Image.open("fishbowl.gif")
    photo = ImageTk.PhotoImage(image)
    photo_label = Label(image=photo)
    photo_label.image = photo # this line need to prevent gc
    photo_label.grid(row=0, column=2, columnspan=7, rowspan=7)

    # Submission
    def my_click():
        my_first_name = first_name.get()
        my_last_name = last_name.get()
        my_email = email.get()
        my_group_name = group_name.get()
        my_room_number = room_number.get()
        my_time = time.get()
        user_info = open("userinfo.txt", "w")
        user_info.writelines('\n'.join([my_first_name, my_last_name, my_email, my_group_name, my_room_number, my_time]))
        user_info.close()
        root.quit()
    my_button = Button(root, text="Submit", command=my_click)
    my_button.grid(row=7, column=1)
    root.mainloop()

# Save user information in text file
user_info = open("userinfo.txt", "r")
user_info_list = user_info.read().splitlines()
user_info.close()

# Assign correct room number and time
time_element_data_locator = time_list.index(user_info_list[5])
time_element_list = []
if user_info_list[4] == "216L":
    time_element_data = open("216L.txt","r")
elif user_info_list[4] == "216N":
    time_element_data = open("216N.txt","r")
elif user_info_list[4] == "216Q":
    time_element_data = open("216Q.txt","r")
else:
    time_element_data = open("216S.txt","r")
for c, value in enumerate(time_element_data.read().splitlines()):
        if c >= time_element_data_locator*3 and c <= time_element_data_locator*3+2:
            time_element_list.append(value)
time_element_data.close()

## Open browser
browser = webdriver.Chrome()
browser.get('http://schedule.lib.calpoly.edu/rooms.php?i=2015')

# Today's date
current_date = datetime.now()
current_month = current_date.strftime("%m")
current_day = current_date.strftime("%d")

# Target date (2 week ahead)
delta_date = timedelta(14)
target_date = current_date + delta_date
target_month = target_date.strftime("%m")
target_day = target_date.strftime("%d")

# Change page if target date is next month
if target_month != current_month and target_day != "14":
    next_button = browser.find_element_by_xpath('//*[@id="s-lc-rm-cal"]/div/div/a[2]/span')
    next_button.click()

# Click on target date
calendar_day = browser.find_element_by_link_text(target_day)
calendar_day.click()
sleep(1)

# Reserve 3 hours
reserve_time_1 = browser.find_element_by_xpath('//*[@data-seq="{}"]'.format(time_element_list[0]))
reserve_time_1.click()
reserve_time_2 = browser.find_element_by_xpath('//*[@data-seq="{}"]'.format(time_element_list[1]))
reserve_time_2.click()
reserve_time_3 = browser.find_element_by_xpath('//*[@data-seq="{}"]'.format(time_element_list[2]))
reserve_time_3.click()

# Fill in form
first_name = browser.find_element_by_xpath('//*[@id="fname"]')
first_name.send_keys(user_info_list[0])
last_name = browser.find_element_by_xpath('//*[@id="lname"]')
last_name.send_keys(user_info_list[1])
email = browser.find_element_by_xpath('//*[@id="email"]')
email.send_keys(user_info_list[2])
group_name = browser.find_element_by_xpath('//*[@id="nick"]')
group_name.send_keys(user_info_list[3])

# Submit
submit = browser.find_element_by_xpath('//*[@id="s-lc-rm-sub"]')
submit.click()