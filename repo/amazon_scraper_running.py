import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


options = Options()
options.add_argument(r"--user-data-dir=C:\selenium_amazon_profile")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

##===================================open product page===================================
PRODUCT_URL = "https://www.amazon.in/Rich-Dad-Poor-Middle-Anniversary/dp/1612681131"
driver.get(PRODUCT_URL)
time.sleep(5)

##===================================GO TO REVIEWS PAGE ===================================

try:
    review_btn = driver.find_element(By.XPATH, "//a[contains(@data-hook,'see-all-reviews')]")
    driver.execute_script("arguments[0].click();", review_btn)
    time.sleep(5)
except:
    print("⚠️ Could not click 'See all reviews'")

print("Current URL:", driver.current_url)

##===================================STORAGE===================================
reviews = []
seen_ids = set()

# ========================
# 5. FUNCTIONS
# ========================

def extract_reviews():
    elements = driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]")

    new_count = 0

    for el in elements:
        rid = el.get_attribute("id")

        if rid and rid not in seen_ids:
            seen_ids.add(rid)

            try:
                text = el.find_element(By.XPATH, ".//span[@data-hook='review-body']").text
            except:
                text = ""

            if text.strip():
                reviews.append(text)
                new_count += 1

    return new_count


def click_expand():
    try:
        btn = driver.find_element(By.XPATH, "//a[@data-hook='show-more-button']")

        old_reviews = len(driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]"))

        driver.execute_script("arguments[0].click();", btn)

        # IMPORTANT: wait for DOM increase, not sleep
        for _ in range(10):
            time.sleep(2)
            new_reviews = len(driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]"))
            if new_reviews > old_reviews:
                print("✅ New reviews loaded:", new_reviews - old_reviews)
                return True

        print("⚠️ No DOM update detected")
        return False

    except Exception as e:
        print("❌ Click failed:", e)
        return False

# ========================
# 6. MAIN LOOP
# ========================
no_change = 0
last_count = 0

for i in range(30):
    print(f"\n🔁 Cycle {i+1}")

    # ---- scroll to trigger lazy load
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    time.sleep(random.uniform(2, 3))

    # ---- extract visible reviews
    new_reviews = extract_reviews()

    print("➕ New reviews this cycle:", new_reviews)
    print("📦 Total collected:", len(reviews))

    # ========================
    # 7. DEBUG + EXPAND LOGIC (IMPORTANT PART)
    # ========================

    before_reviews = len(driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]"))

    clicked = click_expand()

    if clicked:
        time.sleep(5)

    after_reviews = len(driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]"))

    print("📦 Reviews before click:", before_reviews)
    print("📦 Reviews after click:", after_reviews)
    print("📊 New DOM reviews loaded:", after_reviews - before_reviews)

    # ---- stop condition
    if len(reviews) == last_count:
        no_change += 1
    else:
        no_change = 0
        last_count = len(reviews)

    if no_change >= 3:
        print("🚫 No more new reviews loading")
        break

# ========================
# 8. SAVE OUTPUT
# ========================
df = pd.DataFrame({"review": reviews})
df.to_csv("amazon_reviews.csv", index=False)

print("\n🎉 Saved reviews:", len(reviews))

driver.quit()