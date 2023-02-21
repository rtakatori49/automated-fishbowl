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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


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
        self.slot_count = fishbowl["slot_count"]
        self.day_delta = fishbowl["day_delta"]
        email_dict = d["email"]
        self.email = email_dict["user"]
        self.password = email_dict["password"]
        self.link_base = email_dict["link_base"]
        self.operating_system = d["os"]
        self.debug = d["debug"]
        self.academic_calendar = d["academic_calendar"]
config = Config()


# Logging
logger = logging.getLogger(__name__)
def setup_logger(logger):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    if not os.path.isdir('log'):
        os.mkdir('log')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if config.debug:
        file_handler = logging.FileHandler('log/debug.txt')
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler = logging.FileHandler('log/error.txt')
        file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    multiprocessing_logging.install_mp_handler(logger)


def open_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    logger.debug("Browser running headless")
    if config.operating_system == 'windows':
        ser = Service(chromedriver_autoinstaller.install())
    if config.operating_system == 'raspi':
        ser = Service('/usr/lib/chromium-browser/chromedriver')
    logger.debug(f"Operating system: {config.operating_system}")
    browser = webdriver.Chrome(service=ser, options=chrome_options)
    return browser


def user_email_confirm(user):
    user_email = user['email']
    logger.debug(f"Confirming reservation for {user_email}.")
    wait_time = 0
    start_time = time.perf_counter()
    while True:
        logger.debug("Checking email.")
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(config.email, config.password)
        imap.select("inbox", readonly=False)
        today_date = datetime.datetime.now().strftime('%m-%d-%Y')
        _, search_data = imap.search(None, "UNSEEN", f"FROM {user_email}",
            'HEADER subject "Please confirm your booking"', f"SINCE {today_date}")
        if search_data[0].split():
            for num in search_data[0].split():
                _, data = imap.fetch(num, '(RFC822)')
                _, b = data[0]
                email_message = email.message_from_bytes(b)
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain'\
                        or part.get_content_type == 'text/html':
                        body = part.get_payload(decode=True)
                        body_string = body.decode()
                        list_of_link = re.findall(
                            r'(https?://[^\s]+)', body_string)
                        match_list = [match for match in list_of_link
                            if config.link_base in match]
                        link_string = match_list[0]
                        logger.debug(f"Confirmation link: {link_string}.")
                        browser = open_browser()
                        try:
                            logger.debug(f"Opening link {link_string}.")
                            browser.get(link_string)
                            # Submit
                            action = webdriver.ActionChains(browser)
                            submit = browser.find_element(By.XPATH,
                                '//*[@id="rm_confirm_link"]')
                            action.move_to_element(submit)
                            action.click()
                            action.perform()
                            browser.close()
                            logger.debug(
                                f"Confirmation completed for {user_email}.")
                            imap.close()
                        except Exception as e:
                            logger.error(e)
                            imap.close()
            break
        else:
            logger.debug(
                "Confirmation email not found sleeping for 1 minute.")
            time.sleep(60)
            wait_time = time.perf_counter() - start_time
            logger.debug(f"Been sleeping for {wait_time} [s]")
            imap.close()
        if wait_time > 3600:
            logger.error("Email confirmation wait timed out.")
            imap.close()
            break


def get_target_date():
    logger.debug("Getting target date.")
    # Today's date
    current_date = datetime.datetime.now()
    logger.debug(f"Current date: {current_date}")
    # Target date (time defined in config)
    delta_date = datetime.timedelta(config.day_delta)
    target_date = current_date + delta_date
    logger.debug(f"Target date: {target_date}")
    if config.operating_system == 'windows':
        year_string = '%#Y'
        month_string = '%#m'
        day_string = '%#d'
    if config.operating_system == 'raspi':
        year_string = '%-Y'
        month_string = '%-m'
        day_string = '%-d'
    target_year = target_date.strftime(year_string)
    target_month = target_date.strftime(month_string)
    target_day = target_date.strftime(day_string)
    return target_date, target_year, target_month, target_day


def find_date(browser, table_id, target_description):
    try:
        # Find table with date
        start_table = browser.find_element(By.CSS_SELECTOR,
            f'table[id*="{table_id}"]')
        # Get year from table
        table_caption = start_table.find_elements(By.CSS_SELECTOR,
            'caption')[0].text
        year = re.search('\d{4}', table_caption).group(0)
        # Look for month and day from table
        for row in start_table.find_elements(By.CSS_SELECTOR, 'tr'):
            if target_description in row.text:
                cell = row.find_elements(By.CSS_SELECTOR, 'td')[0]
                month_and_day = cell.text
        # Generate datetime
        date_time = datetime.datetime.strptime(f'{month_and_day} {year}',
            '%B %d %Y')
    except Exception as e:
        logger.error(e)
    return date_time


def user_reserve(target_year, target_month,
        target_day, time_assignment, idx, user):
    logger.debug(f"Starting reservation for {user['first_name']}.")
    logger.debug(f"Configuring browser.")
    # Open browser
    browser = open_browser()
    try:
        logger.debug("Opening browser for reservation.")
        browser.get(config.link)
        logger.debug(f"Opening link: {config.link}.")
    except Exception as e:
        logger.error(e)

    # Check page year
    page_year = browser.find_element(
        By.CLASS_NAME, 'ui-datepicker-year').text
    if page_year == target_year:
        same_year = True
        logger.debug("Page on same year.")
    else:
        same_year = False
        logger.debug("Page on different year.")

    # Select target month from dropdown
    if same_year:
        logger.debug("Using dropdown to select month.")
        target_month_dropdown = Select(
            browser.find_element(By.CLASS_NAME, 'ui-datepicker-month'))
        target_month_dropdown.select_by_value(str(int(target_month)-1))
    else:
        logger.debug("Using next button to change month.")
        next_month_button = browser.find_element(
            By.CLASS_NAME, 'ui-icon-circle-triangle-e')
        next_month_button.click()
        time.sleep(1)

    # Click on target date
    logger.debug(f"Selecting date: {target_day}.")
    calendar_day = browser.find_element(By.LINK_TEXT, target_day)
    calendar_day.click()
    time.sleep(1)

    # Reserve 3 hours
    logger.debug("Reserving time.")
    for time_element in time_assignment[idx]:
        try:
            reserve_time = browser.find_element(By.XPATH,
                f"//*[@data-seq={time_element}]")
            reserve_time.click()
        except Exception as e:
            logger.error(e)
        # Fill in form
    try:
        logger.debug("Filling in form.")
        first_name = browser.find_element(By.XPATH, '//*[@id="fname"]')
        first_name.send_keys(user['first_name'])
        last_name = browser.find_element(By.XPATH, '//*[@id="lname"]')
        last_name.send_keys(user['last_name'])
        email = browser.find_element(By.XPATH, '//*[@id="email"]')
        email.send_keys(user['email'])
        group_name = browser.find_element(By.XPATH, '//*[@id="nick"]')
        group_name.send_keys(f"{user['first_name']}'s Study Group")

        # Submit
        logger.debug("Submitting.")
        submit = browser.find_element(By.XPATH, '//*[@id="s-lc-rm-sub"]')
        submit.click()
        browser.close()
        logger.debug(f"Reservation for {user['first_name']} completed.")
        user_email_confirm(user)
    except Exception as e:
        logger.error(e)


# Reservation
def reserve():
    logger.debug("Starting fishbowl reservation.")
    # Assign times to each user
    time_element_base = config.time_element[config.room]
    time_element = range(
        time_element_base,
        time_element_base+config.slot_count)
    time_assignment = np.array_split(time_element, len(config.reserver))
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
    target_date, target_year, target_month, target_day = get_target_date()
    browser = open_browser()
    browser.get(config.academic_calendar['link'])
    start_date = find_date(browser,
        config.academic_calendar['start']['table_id'],
        config.academic_calendar['start']['description'])
    logger.debug(f"School start date: {start_date}")
    end_date = find_date(browser,
        config.academic_calendar['end']['table_id'],
        config.academic_calendar['end']['description'])
    logger.debug(f"School end date: {end_date}")
    try:
        logger.debug("Checking target date against academic calendar.")
        if start_date < target_date and end_date > target_date:
            processes = []
            for idx, user in enumerate(config.reserver):
                p = Process(target=user_reserve, args=(target_year,
                    target_month, target_day, time_assignment, idx,
                    user,))
                p.start()
                processes.append(p)
            for process in processes:
                process.join()
        else:
            raise ValueError('Target day is not a school day.')
    except ValueError as e:
        logger.error(e)
    

def main():
    setup_logger(logger)
    reserve()


if __name__ == "__main__":
    main()