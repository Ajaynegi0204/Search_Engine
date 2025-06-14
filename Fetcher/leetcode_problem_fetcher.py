from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

page_URL = "https://leetcode.com/problemset/"

def get_a_tags(url):
    try:
        driver.get(url)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            for _ in range(10):
                time.sleep(1)  
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height != last_height:
                    break  
            else:
                break  

            last_height = new_height

        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "w-full.pb-\\[80px\\]"))
        )

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

logging.info("Starting to scrape LeetCode problems...")
problem_links = get_a_tags(page_URL)



output_file = '../lc.txt'
with open(output_file, 'w') as f:
    for link in problem_links:
        f.write(link + '\n')

logging.info(f"Total unique links found: {len(problem_links)}")

# Close the browser
driver.quit()
