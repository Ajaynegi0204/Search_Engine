from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the WebDriver using WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Base URL for the LeetCode problem set page
page_URL = "https://leetcode.com/problemset/"

# Function to get all the 'a' tags from the infinite scrolling page
def get_a_tags(url):
    try:
        # Load the URL in the browser
        driver.get(url)

        # Scroll to the bottom of the page to load all content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for a maximum of 10 seconds for new content to load
            for _ in range(10):
                time.sleep(1)  # Check every 1 second
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height != last_height:
                    break  # Exit the loop if new content is loaded
            else:
                break  # Exit the outer loop if no new content is loaded within 10 seconds

            last_height = new_height

        # Locate the specific div by its class name
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "w-full.pb-\\[80px\\]"))
        )

        # Find all 'a' tags within the container
        links = container.find_elements(By.TAG_NAME, "a")

        unique_links = set()
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and "/problems/" in href:
                    unique_links.add(href)
            except Exception as e:
                logging.warning(f"Error processing link: {e}")

        return list(unique_links)
    except Exception as e:
        logging.error(f"Error loading URL {url}: {e}")
        return []
# Get all problem links
logging.info("Starting to scrape LeetCode problems...")
problem_links = get_a_tags(page_URL)




# Write the results to a file
output_file = '../lc.txt'
with open(output_file, 'w') as f:
    for link in problem_links:
        f.write(link + '\n')

logging.info(f"Total unique links found: {len(problem_links)}")

# Close the browser
driver.quit()