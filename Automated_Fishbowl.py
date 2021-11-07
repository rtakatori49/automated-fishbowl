# Automated Fishbowl Reserver
# Ryo Takatori
# 04/06/2020
# Created to automate fishbowl reservation

# Modules
import chromedriver_autoinstaller
import datetime
import json
import time

from selenium import webdriver

# Load json
def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

# Load time element specific to user choice
def get_time_element():
    user_info = load_json("user.json")
    reserve_time = load_json("reserve_time.json")
    time_element = load_json("time_element.json")
    reserve_time_list = reserve_time[user_info["selected_time"]]
    time_element_list = [time_element[user_info["room_name"]][x] for x in reserve_time_list]
    return time_element_list

# Reservation
def reserve():
    # Load user preference
    user_info = load_json("user.json")
    time_element_list = get_time_element()

    ## Open browser
    chromedriver_autoinstaller.install()
    browser = webdriver.Chrome()
    browser.get('http://schedule.lib.calpoly.edu/rooms.php?i=2015')

    # Today's date
    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%m")

    # Target date (2 week ahead)
    delta_date = datetime.timedelta(14)
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
    time.sleep(1)

    # Reserve 3 hours
    for time_element in time_element_list:
        reserve_time = browser.find_element_by_xpath(f"//*[@data-seq={time_element}]")
        reserve_time.click()

    # Fill in form
    first_name = browser.find_element_by_xpath('//*[@id="fname"]')
    first_name.send_keys(user_info["first_name"])
    last_name = browser.find_element_by_xpath('//*[@id="lname"]')
    last_name.send_keys(user_info["last_name"])
    email = browser.find_element_by_xpath('//*[@id="email"]')
    email.send_keys(user_info["email"])
    group_name = browser.find_element_by_xpath('//*[@id="nick"]')
    group_name.send_keys(user_info["group_name"])

    # Submit
    submit = browser.find_element_by_xpath('//*[@id="s-lc-rm-sub"]')
    submit.click()

def main():
    reserve()

if __name__ == "__main__":
    main()