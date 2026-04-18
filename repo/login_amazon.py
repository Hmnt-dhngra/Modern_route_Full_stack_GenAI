from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()

# IMPORTANT: use a clean dedicated profile folder
options.add_argument(r"--user-data-dir=C:\selenium_amazon_profile")

driver = webdriver.Chrome(options=options)

driver.get("https://www.amazon.in/")
time.sleep(60)

