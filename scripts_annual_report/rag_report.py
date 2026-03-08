from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

class AnnualReportRAG:

    def __init__(self):

        print("🔹 Loading embeddings...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        print("🔹 Connecting to Qdrant...")

        self.client = QdrantClient(host="localhost", port=6333)

        self.vectorstore = Qdrant(
            client=self.client,
            collection_name="hsbc_report",
            embeddings=self.embeddings
        )

        print("🔹 Loading LLM...")

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a financial analyst.

Answer the question using ONLY the context from the HSBC annual report.

If the answer is not in the context, say "Not found in report."

Context:
{context}

Question:
{question}

Answer:
"""
        )

    def ask(self, question, k=5):

        docs = self.vectorstore.similarity_search(question, k=k)

        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = self.prompt.format(
            context=context,
            question=question
        )

        response = self.llm.invoke(prompt)

        return response.content, docs