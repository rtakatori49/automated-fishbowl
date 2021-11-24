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
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

def accept_email(config):
    for user in config.reserver:
        user_email = user["email"]
        logger.info(f"Confirming reservation for {user_email}.")
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(config.email, config.password)
        imap.select("inbox")
        _, search_data = imap.search(None, "UNSEEN", f"FROM {user_email}")
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
                    logger.info(f"Confirmation link: {link_string}.")
                    chrome_options = Options()
                    chrome_options.add_argument("--headless")
                    if config.operating_system == "windows":
                        chromedriver_autoinstaller.install()
                        browser = webdriver.Chrome(options=chrome_options)
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
                        logger.info(
                            f"Confirmation completed for {user_email}.")
                    except Exception as e:
                        print(e)
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
    target_day = target_date.strftime("%#d")
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
            logger.info("Opening browser.")
            browser.get(config.link)
        except Exception as e:
            logger.error(e)

        # Change page if target date is next month
        if target_month != current_month and target_day != "13":
            next_button = browser.find_element_by_xpath(
                '//*[@id="s-lc-rm-cal"]/div/div/a[2]/span')
            next_button.click()

        # Click on target date
        print(target_day)
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
        d = config.reserver[idx]
        logger.info(f"Starting reservation for {d['first_name']}.")
        try:
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
        except Exception as e:
            logger.error(e)
    
def main():
    config = Config()
    setup_logger(logger)
    #reserve(config)
    logger.info(
        "Sleeping for 1 minute to allow for confirmation link to appear.")
    time.sleep(60)
    accept_email(config)

if __name__ == "__main__":
    main()
