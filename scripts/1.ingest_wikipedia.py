import wikipedia
from tqdm import tqdm

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

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

client = QdrantClient(host="localhost", port=6333)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

documents = []

print("🔹 Fetching Wikipedia animal pages...")
for topic in tqdm(TOPICS):
    try:
        page = wikipedia.page(topic)
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

Qdrant.from_texts(
    texts=texts,
    embedding=embeddings,
    metadatas=metadatas,
    url="http://localhost:6333",
    collection_name=COLLECTION_NAME,
)

print("✅ Animal ingestion complete")
