import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pickle
import sys

# Set up Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening a browser
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Amazon reviews URL

url = sys.argv[1]
driver.get(url)

# Wait for reviews to load
time.sleep(3)

# Scroll down to load more reviews
for _ in range(3):  # Adjust the range to load more reviews
    driver.execute_script("window.scrollBy(0, 800);")
    time.sleep(2)

# Extracting review texts
reviews = driver.find_elements(By.CSS_SELECTOR, ".review-text-content span")

# Prepare the review data
review_data = []
for index, review in enumerate(reviews, start=1):
    review_data.append({
        "No": index,
        "Review": review.text.strip()
    })

# Save to CSV
with open("amazon_reviews.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["No.", "Review"])
    for row in review_data:
        writer.writerow([row["No"], row["Review"]])

# Save to Pickle
with open("amazon_reviews.pkl", "wb") as pkl_file:
    pickle.dump(review_data, pkl_file)

# Close the browser
driver.quit()