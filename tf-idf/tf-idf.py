import os
import math
import time
import random
import logging
from collections import defaultdict
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from dotenv import load_dotenv
import psycopg2


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 100  # Configurable batch size for DB fetch and Qdrant operations


def connect_db():
    return psycopg2.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname")
    )

class TfIdfProcessor:
    def __init__(self, qdrant_client: QdrantClient, collection_name: str):
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.final_collection_name = "problems_v2"



    def fetch_batches(self, batch_size=BATCH_SIZE):
        conn = connect_db()
        cur = conn.cursor(name="streaming_cursor")
        try:
            cur.execute("SELECT id, problem_statement FROM problems")
            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break
                batch = [(pid, stmt.strip()) for pid, stmt in rows if stmt and stmt.strip()]
                yield batch
        finally:
            cur.close()
            conn.close()

    def build_vocab_and_doc_freq(self):
        """
        First pass: compute document frequency and vocabulary without storing all text.
        Returns total_docs (int), doc_freq (dict), vocab_list (list)
        """
        doc_freq = defaultdict(int)  # in how many documents each word appears
        total_docs = 0
        vocab = set()

        logger.info("Starting first pass: building vocabulary and document frequencies")
        for batch in self.fetch_batches():
            for _, text in batch:
                total_docs += 1
                words = text.split()
                seen = set()
                for w in words:
                    if w not in seen:
                        doc_freq[w] += 1
                        seen.add(w)
                vocab.update(words)

        vocab_list = sorted(vocab)
        logger.info(f"Completed first pass: total docs={total_docs}, vocab size={len(vocab_list)}")
        return total_docs, doc_freq, vocab_list

    def fetch_existing_payloads(self, ids):
        """
        Fetch payloads in batches for given ids from Qdrant.
        Returns dictionary {id: payload}.
        """
        existing_payloads = {}
        logger.info(f"Fetching existing payloads for {len(ids)} points")
        for i in range(0, len(ids), BATCH_SIZE):
            batch_ids = ids[i:i + BATCH_SIZE]
            try:
                points = self.qdrant_client.retrieve(
                    collection_name=self.collection_name,
                    ids=batch_ids,
                    with_payload=True,
                )
                for p in points:
                    existing_payloads[p.id] = p.payload or {}
            except Exception as e:
                logger.error(f"Error retrieving payload batch {batch_ids}: {e}")
        return existing_payloads

    def compute_idf(self, total_docs, doc_freq):
        """Compute IDF score per term."""
        idf = {w: 1 + math.log(total_docs / freq) for w, freq in doc_freq.items()}
        return idf

    def compute_tf_idf_vector(self, word_counts, idf, word2idx):
        """
        Compute TF-IDF vector given word counts, idf dict, and word2idx mapping.
        Returns a list vector of floats.
        """
        total_words = sum(word_counts.values())
        vec = [0.0] * len(word2idx)
        for w, count in word_counts.items():
            idx = word2idx.get(w)
            if idx is not None and total_words > 0:
                tf = count / total_words
                vec[idx] = tf * idf.get(w, 0.0)

        norm = math.sqrt(sum(x*x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def retry_upsert(self, points, max_retries=5, base_delay=2.0):
        """Upsert points into Qdrant with retry logic and exponential backoff."""
        attempt = 0
        while attempt <= max_retries:
            try:
                self.qdrant_client.upsert(collection_name=self.final_collection_name, points=points)
                return
            except Exception as e:
                wait = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                logger.warning(f"Upsert failed (attempt {attempt}): {e}, retrying in {wait:.2f}s")
                time.sleep(wait)
                attempt += 1
        logger.error(f"Failed to upsert points after {max_retries} retries.")

    def process_and_upsert(self):
        """
        Run full two-pass TF-IDF computation and upsert vectors to Qdrant.
        """
        # First pass - get vocab and doc freq
        total_docs, doc_freq, vocab_list = self.build_vocab_and_doc_freq()

        # Prepare ID mapping and IDF scores
        word2idx = {w: i for i, w in enumerate(vocab_list)}
        idf = self.compute_idf(total_docs, doc_freq)

        logger.info("Starting second pass: compute TF-IDF vectors and upsert to Qdrant")

        for batch in self.fetch_batches():
            batch_ids = []
            batch_word_counts = []

            # Prepare per-document word counts in batch
            for pid, text in batch:
                words = text.split()
                wc = defaultdict(int)
                for w in words:
                    wc[w] += 1
                batch_ids.append(pid)
                batch_word_counts.append((pid, wc))

            # Retrieve existing payloads for preservation
            existing_payloads = self.fetch_existing_payloads(batch_ids)

            # Prepare points for upsert
            points_to_upsert = []
            for pid, wc in batch_word_counts:
                vector = self.compute_tf_idf_vector(wc, idf, word2idx)
                payload = existing_payloads.get(pid, {})
                points_to_upsert.append(PointStruct(id=int(pid), vector=vector, payload=payload))

            # Upsert in smaller batches to avoid timeouts
            for i in range(0, len(points_to_upsert), BATCH_SIZE):
                chunk = points_to_upsert[i:i + BATCH_SIZE]
                self.retry_upsert(chunk)
                logger.info(f"Upserted batch of {len(chunk)} vectors")


def create_qdrant_client():
    return QdrantClient(
        url=os.getenv("qdrant_url"),
        api_key=os.getenv("qdrant_apikey"),
        timeout=300.0
    )


def main():
    qdrant_client = create_qdrant_client()
    processor = TfIdfProcessor(qdrant_client=qdrant_client, collection_name="problems")
    processor.process_and_upsert()


if __name__ == "__main__":
    main()