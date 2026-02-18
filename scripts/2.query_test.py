from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

COLLECTION_NAME = "wiki_animals_poc"

print("🔹 Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("🔹 Connecting to Qdrant...")
client = QdrantClient(host="localhost", port=6333)

print("🔹 Loading vector store...")
vector_store = Qdrant(
    client=client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings,
)

query = input("\n🔍 Enter your query: ")

results = vector_store.similarity_search(query, k=5)

print("\n" + "=" * 80)
print(f"Results for query: {query}")
print("=" * 80)

for i, doc in enumerate(results, 1):
    print(f"\nResult {i}")
    print("-" * 40)
    print("Title:", doc.metadata.get("title"))
    print("Chunk ID:", doc.metadata.get("chunk_id"))
    print("Source:", doc.metadata.get("source"))
    print("\nText snippet:")
    print(doc.page_content[:300])
