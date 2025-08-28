import json
import redis
import os
from dotenv import load_dotenv

load_dotenv()


r = redis.Redis(
    host='redis-12077.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=12077,
    decode_responses=True,
    username="default",
    password= os.getenv("redis_password"),
)

# print(os.getenv("redis_password"))

with open("vocab.json", "r") as f:
    vocab_data = json.load(f)
r.set("vocab_json", json.dumps(vocab_data))


with open("idf.json", "r") as f:
    idf_data = json.load(f)
r.set("idf_json", json.dumps(idf_data))

print("✅ Uploaded vocab and idf to Redis!")
