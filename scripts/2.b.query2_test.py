from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Qdrant client
client = QdrantClient(
    host="localhost",
    port=6333
)

# Vector store (NEW API)
vector_store = QdrantVectorStore(
    client=client,
    collection_name="wiki_text_poc",
    embedding=embeddings,
)

query = "difference between machine learning and deep learning"

results = vector_store.similarity_search(query, k=5)

print(f"\n🔍 Query: {query}")
print("=" * 80)

for i, doc in enumerate(results, 1):
    print(f"\nResult {i}")
    print("-" * 40)
    print(f"Chunk ID   : {doc.metadata.get('chunk_id')}")
    print(f"Source URL : {doc.metadata.get('source')}")
    print(f"Text Snippet:\n{doc.page_content[:200]}")
