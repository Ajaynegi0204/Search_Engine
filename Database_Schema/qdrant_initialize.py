from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from dotenv import load_dotenv
import os
load_dotenv()

qdrant_client = QdrantClient(
    url= os.getenv("qdrant_url"),
    api_key= os.getenv("qdrant_apikey"),
)

VOCAB_SIZE = 25602
if not qdrant_client.collection_exists(collection_name="problems_v2"):
    qdrant_client.create_collection(
        collection_name="problems_v2",
        vectors_config=VectorParams(size=VOCAB_SIZE, distance=Distance.COSINE),
    )
else:
    print("Collection already exists")

print(qdrant_client.get_collections())
