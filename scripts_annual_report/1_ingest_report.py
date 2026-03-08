import os
from tqdm import tqdm

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

PDF_PATH = "data/annual_reports/hsbc_annual_report.pdf"

print("📄 Loading PDF...")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print(f"Loaded {len(documents)} pages")

# Better chunking for financial docs
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

print("✂️ Splitting text...")
chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

print("🧠 Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("🔗 Connecting to Qdrant...")
client = QdrantClient(host="localhost", port=6333)

collection_name = "hsbc_report"

print("📥 Uploading embeddings...")
Qdrant.from_documents(
    chunks,
    embeddings,
    url="http://localhost:6333",
    collection_name=collection_name,
)

print("✅ Ingestion complete")