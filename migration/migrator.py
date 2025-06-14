import os
import psycopg2
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct


load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

qdrant_client = QdrantClient(
    url=os.getenv("qdrant_url"),
    api_key=os.getenv("qdrant_apikey"),
    timeout = 300.0
)

collection_name = "problems"


def fetch_all_data():
    logging.info("Connecting to Supabase Postgres database...")
    conn = psycopg2.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname")
    )
    cur = conn.cursor()

    cur.execute("""
                SELECT id, problem_name, problem_link, platform,topics
                FROM problems
                """)

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = []
    for row in rows:
        item = {columns[i]: row[i] for i in range(len(columns))}
        data.append(item)

    return data


import time
import random

def push_to_qdrant(rows, max_retries=5, base_delay=2.0):
    points = []
    for row in rows:
        pid = row.get("id")
        if pid is None:
            continue

        vector_size = 25602
        point = PointStruct(
            id=int(pid),
            vector=[0.0] * vector_size,
            payload=row
        )
        points.append(point)

    BATCH_SIZE = 100
    total = len(points)

    for i in range(0, total, BATCH_SIZE):
        batch = points[i:i + BATCH_SIZE]
        attempt = 0

        while attempt <= max_retries:
            try:
                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                break
            except Exception as e:
                attempt += 1
                wait_time = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                if attempt > max_retries:
                    logging.error(f"Failed to insert batch {i // BATCH_SIZE + 1} after {max_retries} attempts.")
                else:
                    time.sleep(wait_time)

if __name__ == "__main__":
    all_data = fetch_all_data()
    push_to_qdrant(all_data)
