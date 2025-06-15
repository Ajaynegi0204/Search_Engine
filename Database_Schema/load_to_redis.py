import json
import redis

r = redis.Redis(
    host='redis-14042.crce179.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=14042,
    decode_responses=True,
    username="default",
    password="tXnxcUbI5bazp5R8mXtl9qFumLOLBMHA",
)

with open("vocab.json", "r") as f:
    vocab_data = json.load(f)
r.set("vocab_json", json.dumps(vocab_data))


with open("idf.json", "r") as f:
    idf_data = json.load(f)
r.set("idf_json", json.dumps(idf_data))

print("✅ Uploaded vocab and idf to Redis!")
