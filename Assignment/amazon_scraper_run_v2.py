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
        # STEP 1: safely check if button exists
        buttons = driver.find_elements(By.XPATH, "//a[@data-hook='show-more-button']")

        if not buttons:
            print("🚫 No more 'Show more reviews' button found → pagination ended")
            return False  # important: signals STOP to your loop

        btn = buttons[0]

        # STEP 2: count reviews BEFORE click
        old_count = len(driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]"))

        # STEP 3: click using JS (more reliable for Amazon DOM)
        driver.execute_script("arguments[0].click();", btn)

        # STEP 4: wait for DOM update (not fixed sleep dependency)
        for _ in range(10):
            time.sleep(2)

            new_count = len(driver.find_elements(By.XPATH, "//div[contains(@id,'customer_review')]"))

            if new_count > old_count:
                print(f"✅ New reviews loaded: {new_count - old_count}")
                return True  # continue scraping

        print("⚠️ Click happened but no DOM increase detected")
        return False

    except Exception as e:
        print(f"❌ click_expand error: {e}")
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

    

    clicked = click_expand()

    
        

    

    
    
    

    # ---- stop condition
    if len(reviews) == last_count:
        no_change += 1
    else:
        no_change = 0
        last_count = len(reviews)

    if no_change >= 3 and not driver.find_elements(By.XPATH, "//a[@data-hook='show-more-button']"):
        print("🚫 Stable end state reached")
        break

# ========================
# 8. SAVE OUTPUT
# ========================
df = pd.DataFrame({"review_text": reviews})
df.to_csv("amazon_reviews.csv", index=False)

print("\n🎉 Saved reviews:", len(reviews))

driver.quit()