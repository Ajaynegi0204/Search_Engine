import cloudscraper
from bs4 import BeautifulSoup
import logging
import re
import psycopg2
import os
import json
import threading
import queue
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from time import sleep

# Load environment variables
load_dotenv()
batch_size = 50
max_threads = 10
input_file = '../lc.txt'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Clean text
def clean_text(text):
    text = text.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', text).strip()

# Extract problem from LeetCode
def extract_problem_details(slug_url):
    try:
        scraper = cloudscraper.create_scraper()
        graphql_url = "https://leetcode.com/graphql"
        slug = slug_url.rstrip('/').split("/")[-1]

        payload = {
            "operationName": "questionData",
            "variables": {"titleSlug": slug},
            "query": """
            query questionData($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                questionTitle
                content
                topicTags {
                  name
                }
              }
            }
            """
        }

        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/problems/{slug}/",
            "Origin": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0"
        }

        res = scraper.post(graphql_url, json=payload, headers=headers)
        if res.status_code != 200:
            logging.error(f"Failed to fetch {slug_url}: HTTP {res.status_code}")
            return None

        data = res.json()["data"]["question"]
        if not data:
            logging.error(f"No data found for {slug}")
            return None

        return {
            'problem_name': data["questionTitle"],
            'problem_link': slug_url,
            'platform': 'LeetCode',
            'topics': [tag["name"] for tag in data["topicTags"]],
            'problem_statement': clean_text(BeautifulSoup(data["content"], "html.parser").get_text())
        }

    except Exception as e:
        logging.error(f"Error processing {slug_url}: {e}")
        return None

# Insert into DB
def insert_batch(batch):
    try:
        conn = psycopg2.connect(
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port"),
            dbname=os.getenv("dbname")
        )
        cur = conn.cursor()
        insert_query = '''
            INSERT INTO problems (problem_name, problem_link, platform, problem_statement, topics)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (problem_link) DO NOTHING;
        '''
        values = [
            (p['problem_name'], p['problem_link'], p['platform'], p['problem_statement'], p['topics'])
            for p in batch
        ]
        cur.executemany(insert_query, values)
        conn.commit()
        logging.info(f"Inserted batch of size {len(batch)}")
    except Exception as e:
        logging.error(f"DB insert error: {e}")
    finally:
        cur.close()
        conn.close()

# Background thread: collects problems and inserts in batches
def batch_inserter_worker(problem_queue):
    buffer = []
    while True:
        problem = problem_queue.get()
        if problem is None:  # Sentinel value to stop thread
            if buffer:
                insert_batch(buffer)
            break

        buffer.append(problem)
        if len(buffer) >= batch_size:
            insert_batch(buffer)
            buffer = []

# Main function
if __name__ == "__main__":
    problem_queue = queue.Queue()

    # Start the background batch-inserter thread
    inserter_thread = threading.Thread(target=batch_inserter_worker, args=(problem_queue,))
    inserter_thread.start()

    # Read URLs
    urls = []
    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    # Start scraping in parallel
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for url in urls:
            executor.submit(
                lambda u: problem_queue.put(p) if (p := extract_problem_details(u)) else None,
                url
            )

    # Signal end of work
    problem_queue.put(None)
    inserter_thread.join()
