import torch
import open_clip
from qdrant_client import QdrantClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()



class MultimodalRAG:

    def __init__(self):

        print("🔹 Connecting to Qdrant...")
        self.qdrant = QdrantClient(host="localhost", port=6333)

        print("🔹 Loading embedding model...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.text_store = Qdrant(
            client=self.qdrant,
            collection_name="wiki_animals_poc",  # change if needed
            embeddings=embeddings
        )

        print("🔹 Loading CLIP...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.clip_model, _, _ = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="laion2b_s34b_b79k"
        )
        self.tokenizer = open_clip.get_tokenizer("ViT-B-32")

        self.clip_model = self.clip_model.to(self.device)
        self.clip_model.eval()

        print("🔹 Loading Groq LLM...")
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=1024
        )

    def retrieve_text(self, query):

        docs = self.text_store.similarity_search(query, k=3)

        context = "\n\n".join([
            f"{doc.metadata.get('title')}:\n{doc.page_content}"
            for doc in docs
        ])

        return context

    def retrieve_images(self, query):

        tokens = self.tokenizer([query]).to(self.device)

        with torch.no_grad():
            embedding = self.clip_model.encode_text(tokens).cpu().numpy()[0]

        results = self.qdrant.search(
            collection_name="demo_animals",
            query_vector=embedding.tolist(),
            limit=3
        )

        return results

    def answer(self, query):

        print("📚 Retrieving text...")
        docs = self.text_store.similarity_search(query, k=3)

        text_context = "\n\n".join([
            f"[{i+1}] {doc.metadata.get('title', 'Unknown')}:\n{doc.page_content}"
            for i, doc in enumerate(docs)
        ])

        print("🖼 Retrieving images...")
        image_results = self.retrieve_images(query)

        prompt = f"""
    You are a retrieval-augmented assistant.

    ONLY answer using the context below.
    If the answer is not present, say:
    "I could not find this in the knowledge base."

    Context:
    {text_context}

    Question:
    {query}

    Answer with citations like [1], [2].
    """

        response = self.llm.invoke(prompt)

        return response.content, image_results, docs
