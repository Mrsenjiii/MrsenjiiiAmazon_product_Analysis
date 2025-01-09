import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize the Chrome browser driver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless to avoid opening the browser window
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL of the product
url = """https://www.amazon.in/Portronics-Wireless-Optical-Orientation-Adjustable/dp/B0B296NTFV/ref=cm_cr_arp_d_product_top?ie=UTF8"""
reviews_dict = {5: [], 4: [], 3: [], 2: [], 1: []}

# Open the initial page
driver.get(url)

# Go to all reviews page
link_element = driver.find_element(By.CSS_SELECTOR, 'a[data-hook="see-all-reviews-link-foot"]')
link_element.click()

# Wait for the full page to load
time.sleep(5)

# Function to get the next page URL
def another_page_url(driver):
    try:
        ul = driver.find_element(By.CSS_SELECTOR, 'ul.a-pagination')
        next_page_li_s_html = ul.get_attribute('outerHTML')
        soup = BeautifulSoup(next_page_li_s_html, 'html.parser')
        next_li = soup.find_all('li', class_='a-last')
        if next_li and next_li[0].find('a'):
            return next_li[0].find('a')['href']
        else:
            return False
    except Exception as e:
        print("Error in getting next page URL:", e)
        return None

# Function to scrape reviews and handle pagination
def scrape_reviews(link, star_rating):
    link = link
    while link :
        driver.get(link)
        time.sleep(3)  # Let the page load
        try:
            reviews = driver.find_elements(By.CSS_SELECTOR, 'div[data-hook="review"]')
            for review in reviews:
                review_text = review.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]').text
                reviews_dict[star_rating].append(review_text)  # Append the review text to the list

            # Get the next page URL
            next_page_relative_url = another_page_url(driver)
            print(next_page_relative_url)
        
            if next_page_relative_url:
                link = "https://www.amazon.in" + next_page_relative_url
            else:
                return None
        except Exception as e:
            print(f"Error scraping reviews for {star_rating} star rating: {e}")
            break

# Scrape reviews for each star rating (5 to 1 stars)

# Get the histogram table and all star rating links
ul_element = driver.find_element(By.ID, "histogramTable")
a_tags = ul_element.find_elements(By.TAG_NAME, "a")
hrefs= []

for a_tag in a_tags :
    # print(a_tag.get_attribute("href"))
    hrefs.append(a_tag.get_attribute("href"))

    


star_rating = 5
for link in hrefs :
        try : 
            print(link , star_rating)
            scrape_reviews(link,star_rating)  # Scrape reviews for this star rating
            star_rating = star_rating - 1
        except Exception as e:
                print(f"Error processing {star_rating} star link after retries: {e}")

# Print all collected reviews
for star, reviews in reviews_dict.items():
    print(f"Reviews for {star} stars:")
    print(star, len(reviews))
    
# Optionally close the driver
driver.quit()