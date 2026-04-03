import wikipedia
from tqdm import tqdm

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance


COLLECTION_NAME = "wiki_animals_poc"

TOPICS = [
    "Cat",
    "Dog",
    "Lion",
    "Tiger",
    "Elephant",
    "Giraffe",
    "Zebra",
    "Horse",
    "Bear",
    "Wolf",
    "Fox",
    "Leopard",
    "Cheetah",
    "Kangaroo",
    "Panda",
    "Penguin",
    "Dolphin",
    "Whale",
    "Rabbit",
    "Deer"
]

print("🔹 Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# client = QdrantClient(host="localhost", port=6333)
client = QdrantClient(":memory:")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

documents = []

print("🔹 Fetching Wikipedia animal pages...")
for topic in tqdm(TOPICS):
    try:
        search_results = wikipedia.search(topic)

        if not search_results:
            print(f"⚠️ No results for {topic}")
            continue

        # pick the most relevant result
        page = wikipedia.page(title=search_results[0], auto_suggest=False)

        print(f"✅ Loaded: {page.title}")

        chunks = splitter.split_text(page.content)

        for i, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "metadata": {
                    "title": page.title,
                    "source": page.url,
                    "chunk_id": i
                }
            })

    except Exception as e:
        print(f"⚠️ Skipped {topic}: {e}")

texts = [d["text"] for d in documents]
metadatas = [d["metadata"] for d in documents]

print(f"🔹 Uploading {len(texts)} chunks to Qdrant...")

# Step 1: Create collection
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)

db = Qdrant(
    client=client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings,
)

db.add_texts(
    texts=texts,
    metadatas=metadatas
)

print("✅ Animal ingestion complete")
