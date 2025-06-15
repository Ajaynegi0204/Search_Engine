from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import cloudscraper
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

base_url = "https://codeforces.com/problemset/page/"


def get_links_from_page(url):
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)

        if response.status_code == 200:
            driver.get("data:text/html;charset=utf-8," + response.text)
            
            links = driver.find_elements(By.CSS_SELECTOR, "table.problems a")  
            
            problem_links = set()
            for link in links:
                href = link.get_attribute('href')
                if href and "/problemset/problem/" in href:
                    problem_links.add(href)

            return problem_links
        else:
            logging.error(f"Failed to fetch URL {url}: HTTP {response.status_code}")
            return set()
    except Exception as e:
        logging.error(f"Error loading URL {url}: {e}")
        return set()

logging.info("Starting to scrape Codeforces problems...")
all_links = set()
for page in range(1, 6):  
    page_url = f"{base_url}{page}"
    logging.info(f"Scraping page: {page_url}")
    all_links.update(get_links_from_page(page_url))

output_file = 'codeforces1.txt'
with open(output_file, 'w') as f:
    for link in sorted(all_links):
        f.write(link + '\n')

logging.info(f"Total unique links found: {len(all_links)}")


driver.quit()
