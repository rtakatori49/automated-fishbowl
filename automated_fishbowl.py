# Automated Fishbowl Reserver
# Ryo Takatori
# 04/06/2020
# Created to automate fishbowl reservation

# Modules
import chromedriver_autoinstaller
import datetime
import email
import json
import imaplib
import logging
import multiprocessing_logging
import numpy as np
import os
import re
import time

from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Load json
def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

class Config:
    def __init__(self):
        d = load_json("config.json")
        self.reserver = d["reserver"]
        self.time_element = d["time_element"]
        fishbowl = d["fishbowl"]
        self.link = fishbowl["link"]
        self.room = fishbowl["room"]
        self.time = fishbowl["time"]
        email_dict = d["email"]
        self.email = email_dict["user"]
        self.password = email_dict["password"]
        self.link_base = email_dict["link_base"]
        self.operating_system = d["os"]
        self.debug = d["debug"]
config = Config()

# Logging
logger = logging.getLogger(__name__)
def setup_logger(logger):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
    if not os.path.isdir("log"):
        os.mkdir("log")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if config.debug:
        file_handler = logging.FileHandler("log/debug.txt")
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler = logging.FileHandler("log/error.txt")
        file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    multiprocessing_logging.install_mp_handler(logger)

def user_email_confirm(user):
    user_email = user["email"]
    logger.debug(f"Confirming reservation for {user_email}.")
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(config.email, config.password)
    imap.select("inbox")
    while True:
        _, search_data = imap.search(None, "UNSEEN", f"FROM {user_email}",
            'HEADER subject "Please confirm your booking"')
        if search_data[0].split():
            for num in search_data[0].split():
                _, data = imap.fetch(num, '(RFC822)')
                _, b = data[0]
                email_message = email.message_from_bytes(b)
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain"\
                        or part.get_content_type == "text/html":
                        body = part.get_payload(decode=True)
                        body_string = body.decode()
                        list_of_link = re.findall(
                            r'(https?://[^\s]+)', body_string)
                        match_list = [match for match in list_of_link
                            if config.link_base in match]
                        link_string = match_list[0]
                        logger.debug(f"Confirmation link: {link_string}.")
                        chrome_options = Options()
                        chrome_options.add_argument("--headless")
                        if config.operating_system == "windows":
                            chromedriver_autoinstaller.install()
                            browser = webdriver.Chrome(
                                options=chrome_options)
                        if config.operating_system == "raspi":
                            browser = webdriver.Chrome(
                                "/usr/lib/chromium-browser/chromedriver",
                                options=chrome_options)
                        try:
                            browser.get(link_string)
                            # Submit
                            action = webdriver.ActionChains(browser)
                            submit = browser.find_element_by_xpath(
                                '//*[@id="rm_confirm_link"]')
                            action.move_to_element(submit)
                            action.click()
                            action.perform()
                            browser.close()
                            logger.debug(
                                f"Confirmation completed for {user_email}.")
                        except Exception as e:
                            print(e)
            break
        else:
            logger.debug(
                "Confirmation email not found sleeping for 1 minute.")
            time.sleep(60)
    imap.close()

def email_confirm():
    processes = []
    for user in config.reserver:
        print(user)
        p = Process(target=user_email_confirm, args=(user,))
        print(p)
        p.start()
        processes.append(p)
    for process in processes:
        print("joining")
        process.join()

def get_target_date():
    logger.debug("Getting target date.")
    # Today's date
    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%m")

    # Target date (2 week ahead)
    delta_date = datetime.timedelta(14)
    target_date = current_date + delta_date
    if config.operating_system == "windows":
        month_string = "%#m"
        day_string = "%#d"
    if config.operating_system == "raspi":
        month_string = "%-m"
        day_string = "%-d"
    target_month = target_date.strftime(month_string)
    target_day = target_date.strftime(day_string)
    return current_month, target_month, target_day

def user_reserve(target_month, current_month, target_day,
    time_assignment, idx, user):
    # Open browser
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        if config.operating_system == "windows":
            chromedriver_autoinstaller.install()
            browser = webdriver.Chrome(options=chrome_options)
        if config.operating_system == "raspi":
            pass
            browser = webdriver.Chrome(
                "/usr/lib/chromium-browser/chromedriver",
                options=chrome_options)
        try:
            logger.debug("Opening browser.")
            browser.get(config.link)
        except Exception as e:
            logger.error(e)

        # Change page if target date is next month
        if target_month != current_month and target_day != "13":
            next_button = browser.find_element_by_xpath(
                '//*[@id="s-lc-rm-cal"]/div/div/a[2]/span')
            next_button.click()

        # Click on target date
        calendar_day = browser.find_element_by_link_text(target_day)
        calendar_day.click()
        time.sleep(1)

        # Reserve 3 hours
        time_element_list = [config.time_element[config.room][str(x)]
            for x in time_assignment[idx]]
        for time_element in time_element_list:
            try:
                reserve_time = browser.find_element_by_xpath(
                    f"//*[@data-seq={time_element}]")
                reserve_time.click()
            except Exception as e:
                logger.error(e)
         # Fill in form
        logger.debug(f"Starting reservation for {user['first_name']}.")
        try:
            first_name = browser.find_element_by_xpath('//*[@id="fname"]')
            first_name.send_keys(user["first_name"])
            last_name = browser.find_element_by_xpath('//*[@id="lname"]')
            last_name.send_keys(user["last_name"])
            email = browser.find_element_by_xpath('//*[@id="email"]')
            email.send_keys(user["email"])
            group_name = browser.find_element_by_xpath('//*[@id="nick"]')
            group_name.send_keys(f"{user['first_name']}'s Study Group")

            # Submit
            submit = browser.find_element_by_xpath('//*[@id="s-lc-rm-sub"]')
            submit.click()
            browser.close()
            logger.debug(f"Reservation for {user['first_name']} completed.")
        except Exception as e:
            logger.error(e)

# Reservation
def reserve():
    logger.debug("Starting fishbowl reservation.")
    # Assign times to each user
    time_assignment = np.array_split(config.time, len(config.reserver))
    # Make sure there are enough users to fill 3 times slots per user
    logger.debug("Assigning time to each user.")
    for assignment in time_assignment:
        try:
            if len(assignment) > 3:
                raise ValueError(
                    "There are not enough reservers." \
                    "Please add more in /config/reserver.json.")
        except ValueError as e:
            logger.error(e)
    # Get target date
    current_month, target_month, target_day = get_target_date()
    processes = []
    for idx, user in enumerate(config.reserver):
        p = Process(target=user_reserve, args=(
            target_month, current_month, target_day,
            time_assignment, idx, user,))
        p.start()
        processes.append(p)
    for process in processes:
        process.join()
    
def main():
    setup_logger(logger)
    reserve()
    email_confirm()

if __name__ == "__main__":
    main()
