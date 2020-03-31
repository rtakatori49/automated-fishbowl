from selenium import webdriver
from datetime import datetime, timedelta

chromedriver = 'C:\\Users\\rtold\\Downloads\\chromedriver'
browser = webdriver.Chrome(chromedriver)
browser.get('http://schedule.lib.calpoly.edu/rooms.php?i=2015')

current_date = datetime.now()
current_month = current_date.strftime("%m")
current_day = current_date.strftime("%d")
delta_date = timedelta(14)
target_date = current_date + delta_date
target_month = target_date.strftime("%m")
target_day = target_date.strftime("%d")
if target_month != current_month:
    next_button = browser.find_element_by_xpath('//*[@id="s-lc-rm-cal"]/div/div/a[2]/span')
    next_button.click()
calendar_day = browser.find_element_by_link_text(target_day)
calendar_day.click()