import psycopg2
import os
import re
import logging
from dotenv import load_dotenv
import nltk
from nltk.corpus import stopwords

# Load environment variables
load_dotenv()

# Download stopwords if not already
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Custom DSA buzzwords to remove
buzzwords = {
    "given", "print", "find", "determine", "check", "output", "input", "consists",
    "contains", "return", "provided", "write", "read", "you", "your", "are", "task",
    "function", "implement", "should", "must", "need", "program", "statement",
    "constraint", "constraints", "example", "note", "format", "description",
    "help", "generate", "value", "values", "used", "using", "new", "valid", "used",
    "provide", "solve", "required", "output", "true", "false", "print", "yes", "no",
    "type", "range", "initialize", "given", "determine", "based", "result", "initialize",
    "whether", "return", "returns", "represent", "represented", "given", "calculate"
}


BATCH_SIZE = 100

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    text = text.encode('ascii', 'ignore').decode('ascii')  # Remove non-ascii
    text = re.sub(r'<[^>]+>', ' ', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)  # Remove punctuation/numbers
    text = text.lower()
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words and t not in buzzwords]
    return ' '.join(tokens)

def connect_db():
    return psycopg2.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname")
    )

def update_problem_statements():
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Fetch id, raw statement, and topics
        cur.execute("SELECT id, problem_statement, topics FROM problems")
        all_rows = cur.fetchall()
        logging.info(f"Fetched {len(all_rows)} rows")

        updates = []
        for idx, (pid, statement, topics) in enumerate(all_rows):
            # Combine statement with topics (make topics a string)
            combined_text = f"{statement or ''} {' '.join(topics or [])}"
            cleaned = clean_text(combined_text)
            updates.append((cleaned, pid))

            if len(updates) == BATCH_SIZE or idx == len(all_rows) - 1:
                cur.executemany("UPDATE problems SET problem_statement = %s WHERE id = %s", updates)
                conn.commit()
                logging.info(f"Updated batch of {len(updates)} rows")
                updates = []

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_problem_statements()
