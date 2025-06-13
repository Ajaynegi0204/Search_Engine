import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to the database
conn = psycopg2.connect(
    user=os.getenv("user"),
    password=os.getenv("password"),
    host=os.getenv("host"),
    port=os.getenv("port"),
    dbname=os.getenv("dbname")
)

cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS problems;")

# SQL statement to create the table
create_table_query = '''
CREATE TABLE IF NOT EXISTS problems (
    id SERIAL PRIMARY KEY,
    problem_name TEXT NOT NULL,
    problem_link TEXT UNIQUE NOT NULL,
    platform TEXT NOT NULL,
    problem_statement TEXT,
    topics TEXT[]  -- Array of text topics
);
'''

# Execute and commit
cur.execute(create_table_query)
conn.commit()

print("Table created successfully!")

# Clean up
cur.close()
conn.close()
