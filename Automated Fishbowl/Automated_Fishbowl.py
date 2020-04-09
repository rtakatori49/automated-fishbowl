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

# chromedriver = 'C:\\Users\\rtold\\Downloads\\chromedriver'
file_exists = os.path.isfile("userinfo.txt")
if not file_exists:
    window = Tk()
    window.title("Automated Fishbowl Reserver")
    grid_title = Label(window, text="Please enter your information:")
    first_name_label = Label(window, text="First Name:")
    last_name_label = Label(window, text="Last Name:")
    email_label = Label(window, text="Email")
    group_name_label = Label(window, text="Group Name:")

    grid_title.grid(row=0, column=0, columnspan=2)
    first_name_label.grid(row=1, column=0)
    last_name_label.grid(row=2, column=0)
    email_label.grid(row=3, column=0)
    group_name_label.grid(row=4, column=0)

    first_name_input = Entry(window, width=15)
    last_name_input = Entry(window, width=15)
    email_input = Entry(window, width=15)
    group_name_input = Entry(window, width=15)

    first_name_input.grid(row=1, column=1)
    last_name_input.grid(row=2, column=1)
    email_input.grid(row=3, column=1)
    group_name_input.grid(row=4, column=1)

    def my_click():
        my_first_name = first_name_input.get()
        my_last_name = last_name_input.get()
        my_email = email_input.get()
        my_group_name = group_name_input.get()
        user_info = open("userinfo.txt", "w")
        user_info.writelines('\n'.join([my_first_name, my_last_name, my_email, my_group_name]))
        user_info.close()
        window.quit()
    my_button = Button(window, text="Submit", command=my_click)
    my_button.grid(row=5, column=0)
    window.mainloop()
user_info = open("userinfo.txt", "r")
user_info_list = []
for x in user_info:
    user_info_list.append(x)
user_info.close()
chromedriver = 'D:\\Downloads\\chromedriver'
browser = webdriver.Chrome(chromedriver)
browser.get('http://schedule.lib.calpoly.edu/rooms.php?i=2015')
current_date = datetime.now()
current_month = current_date.strftime("%m")
current_day = current_date.strftime("%d")
delta_date = timedelta(14)
target_date = current_date + delta_date
target_month = target_date.strftime("%m")
target_day = target_date.strftime("%d")
if target_month != current_month and target_day != "14":
    next_button = browser.find_element_by_xpath('//*[@id="s-lc-rm-cal"]/div/div/a[2]/span')
    next_button.click()
calendar_day = browser.find_element_by_link_text(target_day)
calendar_day.click()
sleep(1)
reserve_time_1 = browser.find_element_by_xpath('//*[@data-seq="5414101"]')
reserve_time_1.click()
reserve_time_2 = browser.find_element_by_xpath('//*[@data-seq="5414102"]')
reserve_time_2.click()
reserve_time_3 = browser.find_element_by_xpath('//*[@data-seq="5414103"]')
reserve_time_3.click()
first_name = browser.find_element_by_xpath('//*[@id="fname"]')
first_name.send_keys(user_info_list[0])
last_name = browser.find_element_by_xpath('//*[@id="lname"]')
last_name.send_keys(user_info_list[1])
email = browser.find_element_by_xpath('//*[@id="email"]')
email.send_keys(user_info_list[2])
group_name = browser.find_element_by_xpath('//*[@id="nick"]')
group_name.send_keys(user_info_list[3])