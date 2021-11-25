import chromedriver_autoinstaller
import time
from multiprocessing import Process
from selenium import webdriver

def open_browser():
    chromedriver_autoinstaller.install()
    browser = webdriver.Chrome()
    browser.get("https://google.com")
    time.sleep(10)

def main():
    p1 = Process(target=open_browser)
    p2 = Process(target=open_browser)
    p1.start()
    p2.start()

if __name__ == "__main__":
    main()