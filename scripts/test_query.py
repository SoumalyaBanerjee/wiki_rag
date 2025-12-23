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

query = "What is deep learning?"

results = vector_store.similarity_search(query, k=3)

for i, doc in enumerate(results, 1):
    print(f"\nResult {i}")
    print(doc.page_content[:300])
    print("Source:", doc.metadata["source"])
