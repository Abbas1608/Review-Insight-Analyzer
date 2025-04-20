import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_product_price(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        
        # Wait for price elements to load
        wait = WebDriverWait(driver, 10)
        
        # Updated list of price selectors
        price_selectors = [
            "span.a-price-whole",
            "span.a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "span.a-color-price",
            "span[data-a-color='price'] span.a-offscreen",
            "#corePrice_desktop span.a-offscreen",
            "span.a-price span[aria-hidden='true']",
            "span.a-price-whole",
            "#price span.a-text-price",
            "#price_inside_buybox",
            "#newBuyBoxPrice",
            "#priceblock_saleprice"
        ]
        
        for selector in price_selectors:
            try:
                # Wait for element and get its text
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                price_text = element.get_attribute('textContent') or element.text
                price_text = price_text.strip()
                
                # Skip empty or invalid price texts
                if not price_text or price_text.lower() in ['currently unavailable', 'not available']:
                    continue
                
                # Clean up the price text
                # Remove currency symbols and non-price text
                price_text = price_text.replace('₹', '').replace('Rs.', '').replace('INR', '').strip()
                price_text = price_text.replace(',', '').replace(' ', '')
                
                # Extract numbers and decimal point
                price_text = ''.join(c for c in price_text if c.isdigit() or c == '.')
                
                # Handle cases where there might be multiple dots
                if price_text.count('.') > 1:
                    price_text = price_text.replace('.', '', price_text.count('.') - 1)
                
                if price_text:
                    try:
                        price = float(price_text)
                        if price > 0:  # Validate price is positive
                            print(f"Price found using selector {selector}: {price}")
                            driver.quit()
                            return price
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        # If no price found with selectors, try finding any price-like text
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for price patterns in the entire page
        price_patterns = []
        
        # Find elements containing currency symbols
        for currency in ['₹', 'Rs.', 'INR']:
            elements = soup.find_all(text=lambda text: text and currency in text)
            price_patterns.extend(elements)
        
        for pattern in price_patterns:
            try:
                price_text = pattern.strip()
                # Remove currency symbols and clean up
                price_text = price_text.replace('₹', '').replace('Rs.', '').replace('INR', '').strip()
                price_text = price_text.replace(',', '').replace(' ', '')
                
                # Extract numbers and decimal point
                price_text = ''.join(c for c in price_text if c.isdigit() or c == '.')
                
                # Handle cases where there might be multiple dots
                if price_text.count('.') > 1:
                    price_text = price_text.replace('.', '', price_text.count('.') - 1)
                
                if price_text:
                    try:
                        price = float(price_text)
                        if price > 0:  # Validate price is positive
                            print(f"Price found from pattern: {price}")
                            driver.quit()
                            return price
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Error parsing price pattern: {e}")
                continue
        
        print("No valid price found")
        driver.quit()
        return None
        
    except Exception as e:
        print(f"Error fetching price: {e}")
        try:
            driver.quit()
        except:
            pass
        return None

def track_price(url, interval_hours=24):
    while True:
        current_price = get_product_price(url)
        if current_price:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Load existing price history
            try:
                with open('price_history.json', 'r') as f:
                    price_history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                price_history = []
            
            # Add new price entry
            price_history.append({
                'timestamp': timestamp,
                'price': current_price
            })
            
            # Save updated price history
            with open('price_history.json', 'w') as f:
                json.dump(price_history, f, indent=4)
            
            print(f"Price tracked at {timestamp}: ₹{current_price}")
        
        time.sleep(interval_hours * 3600)  # Convert hours to seconds

def get_price_history():
    try:
        with open('price_history.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_price_change():
    price_history = get_price_history()
    if len(price_history) < 2:
        return None

    # Calculate difference in price over the time
    current_price = price_history[-1]['price']
    previous_price = price_history[-2]['price']
    change = current_price - previous_price
    percentage_change = (change / previous_price) * 100

    # Load the change in json file
    return {
        'change': change,
        'percentage_change': percentage_change,
        'is_positive': change > 0
    } 
