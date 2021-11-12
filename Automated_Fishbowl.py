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
import numpy as np
import os
import time

from selenium import webdriver

# Logging
logger = logging.getLogger(__name__)
def setup_logger(logger):
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
    if not os.path.isdir("log"):
            os.mkdir("log")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler("log/error.txt")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Load json
def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

class Config:
    def __init__(self):
        self.reserver = load_json("config/reserver.json")
        self.time_element = load_json("config/time_element.json")
        fishbowl = load_json("config/fishbowl.json")
        self.link = fishbowl["link"]
        self.room = fishbowl["room"]
        self.time = fishbowl["time"]
        email_dict = load_json("config/email.json")
        self.email = email_dict["email"]
        self.password = email_dict["password"]
        self.link_base = email_dict["link_base"]
        self.link_string_length = email_dict["link_string_length"]

def accept_email(config):
    for user in config.reserver:
        user_email = config.reserver[user]["email"]
        logger.info(f"Confirming reservation for {user_email}.")
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(config.email, config.password)
        imap.select("inbox")
        _, search_data = imap.search(None, f"FROM {user_email}")
        for num in search_data[0].split():
            _, data = imap.fetch(num, '(RFC822)')
            _, b = data[0]
            email_message = email.message_from_bytes(b)
            for part in email_message.walk():
                if part.get_content_type() == "text/plain"\
                    or part.get_content_type == "text/html":
                    body = part.get_payload(decode=True)
                    body_string = body.decode()
                    link_index = body_string.index(
                        "http://schedule.lib.calpoly.edu/confirm.php")
                    link_string = body_string[link_index:link_index+88]
                    logger.info(f"Confirmation link: {link_string}.")
                    chromedriver_autoinstaller.install()
                    browser = webdriver.Chrome()
                    try:
                        browser.get(link_string)
                    except Exception as e:
                        print(e)
                    # Submit
                    submit = browser.find_element_by_xpath(
                        '//*[@id="rm_confirm_link"]')
                    submit.click()
                    browser.close()
                    logger.info(f"Confirmation completed for {user_email}.")
        imap.close()

def get_target_date():
    logger.info("Getting target date.")
    # Today's date
    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%m")

    # Target date (2 week ahead)
    delta_date = datetime.timedelta(14)
    target_date = current_date + delta_date
    target_month = target_date.strftime("%m")
    target_day = target_date.strftime("%d")
    return current_month, target_month, target_day

# Reservation
def reserve(config):
    logger.info("Starting fishbowl reservation.")
    # Assign times to each user
    time_assignment = np.array_split(config.time, len(config.reserver))
    # Make sure there are enough users to fill 3 times slots per user
    logger.info("Assigning time to each user.")
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
    for idx, user in enumerate(config.reserver):
        ## Open browser
        chromedriver_autoinstaller.install()
        browser = webdriver.Chrome()
        try:
            logger.info("Opening browser.")
            browser.get(config.link)
        except Exception as e:
            logger.error(e)

        # Change page if target date is next month
        if target_month != current_month and target_day != "14":
            next_button = browser.find_element_by_xpath(
                '//*[@id="s-lc-rm-cal"]/div/div/a[2]/span')
            next_button.click()

        # Click on target date
        calendar_day = browser.find_element_by_link_text(target_day)
        calendar_day.click()
        time.sleep(1)

        # Reserve 3 hours
        time_element_list = [config.time_element[config.room][str(x)] for x in time_assignment[idx]]
        for time_element in time_element_list:
            try:
                reserve_time = browser.find_element_by_xpath(
                    f"//*[@data-seq={time_element}]")
                reserve_time.click()
            except Exception as e:
                logger.error(e)
                
        # Fill in form
        d = config.reserver[user]
        logger.info(f"Starting reservation for {d['first_name']}.")
        first_name = browser.find_element_by_xpath('//*[@id="fname"]')
        first_name.send_keys(d["first_name"])
        last_name = browser.find_element_by_xpath('//*[@id="lname"]')
        last_name.send_keys(d["last_name"])
        email = browser.find_element_by_xpath('//*[@id="email"]')
        email.send_keys(d["email"])
        group_name = browser.find_element_by_xpath('//*[@id="nick"]')
        group_name.send_keys(f"{d['first_name']}'s Study Group")

        # Submit
        submit = browser.find_element_by_xpath('//*[@id="s-lc-rm-sub"]')
        submit.click()
        browser.close()
        logger.info(f"Reservation for {d['first_name']} completed.")
    
def main():
    config = Config()
    setup_logger(logger)
    reserve(config)
    accept_email(config)

if __name__ == "__main__":
    main()