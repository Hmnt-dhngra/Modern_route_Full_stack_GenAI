import time
import random
import pandas as pd
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# ========================
# SETUP
# ========================
options = Options()
options.add_argument(r"--user-data-dir=C:\selenium_amazon_profile")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)


PRODUCT_URL = "https://www.amazon.in/Rich-Dad-Poor-Middle-Anniversary/dp/1612681131"
driver.get(PRODUCT_URL)
time.sleep(5)


# ========================
# OPEN REVIEWS
# ========================
def open_reviews():
    try:
        btn = driver.find_element(By.XPATH, "//a[contains(@data-hook,'see-all-reviews')]")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(5)
        return True
    except:
        return False


open_reviews()


# ========================
# STORAGE
# ========================
reviews = []
seen = set()


def h(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ========================
# EXTRACT
# ========================
def extract():
    elements = driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]")

    new = 0

    for el in elements:
        try:
            text = el.find_element(By.XPATH, ".//span[@data-hook='review-body']").text.strip()
        except:
            continue

        if not text:
            continue

        hh = h(text)

        if hh not in seen:
            seen.add(hh)
            reviews.append(text)
            new += 1

    return new


# ========================
# CLICK SHOW MORE
# ========================
def click_show_more():
    btn = driver.find_elements(By.XPATH, "//a[@data-hook='show-more-button']")

    if btn:
        driver.execute_script("arguments[0].click();", btn[0])
        time.sleep(random.uniform(3, 5))
        return True

    return False


# ========================
# FALLBACK: REOPEN FULL REVIEW LIST
# ========================
def reopen_full_reviews():
    try:
        link = driver.find_elements(By.XPATH, "//a[contains(@href,'cm_cr_arp_d_viewopt')]")

        if link:
            driver.execute_script("arguments[0].click();", link[0])
            time.sleep(5)
            return True

        return False
    except:
        return False


# ========================
# MAIN LOOP
# ========================
TARGET = 120

no_progress = 0
last_len = 0

for i in range(60):

    print(f"\n🔁 Cycle {i+1}")
    print(f"📦 Reviews: {len(reviews)}")

    new = extract()
    print("➕ New:", new)

    clicked = click_show_more()

    if not clicked:
        print("⚠️ show-more gone → trying fallback navigation")

        reopened = reopen_full_reviews()

        if reopened:
            print("🔄 Reopened full review page")
        else:
            print("🚫 No fallback available")

    if len(reviews) >= TARGET:
        print("🎯 Target reached")
        break

    if len(reviews) == last_len:
        no_progress += 1
    else:
        no_progress = 0
        last_len = len(reviews)

    if no_progress >= 3:
        print("🚫 No progress detected → stopping")
        break


# ========================
# SAVE
# ========================
df = pd.DataFrame({"review": reviews[:TARGET]})
df.to_csv("amazon_reviews.csv", index=False)

print("\n🎉 Final count:", len(df))

driver.quit()