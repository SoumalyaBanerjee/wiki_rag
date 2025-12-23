import wikipedia
from tqdm import tqdm

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

COLLECTION_NAME = "wiki_text_poc"

TOPICS = [
    "Artificial intelligence",
    "Machine learning",
    "Deep learning",
    "Neural networks",
    "Computer vision",
    "Natural language processing",
    "Data science",
    "Big data",
    "Cloud computing",
    "Python programming",
] * 10  # 100 pages

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

print("🔹 Fetching Wikipedia pages...")
for topic in tqdm(TOPICS):
    try:
        page = wikipedia.page(topic)
        chunks = splitter.split_text(page.content)
        for chunk in chunks:
            documents.append({
                "text": chunk,
                "metadata": {
                    "title": page.title,
                    "source": page.url
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

print("✅ Phase 1 ingestion complete")
