Next Steps :

1. Try multimodal models
2. give a check on more models
3. use a model to get the images plus text

<img width="463" height="181" alt="image" src="https://github.com/user-attachments/assets/002cf306-46bd-4a7a-b635-8cc2f0486f8c" />


🧩 PHASE 1 — TEXT RAG (RECAP DIAGRAM)


<img width="475" height="714" alt="image" src="https://github.com/user-attachments/assets/6388df99-5c31-49ae-8f41-5f53254d6892" />
<img width="402" height="734" alt="image" src="https://github.com/user-attachments/assets/6ef63057-64bb-4f21-8640-0cefbcc48fa3" />



🧠 PHASE 1 — FLOW EXPLAINED IN SIMPLE WORDS
1️⃣ Data ingestion

You pulled Wikipedia articles using the wikipedia Python library.

2️⃣ Chunking (why this matters)

LLMs and embedding models:

Cannot handle very long text

Work best on 500–1,000 token chunks

So you split each article into:

[ chunk 1 ][ chunk 2 ][ chunk 3 ] ...


This allows:

Fine-grained retrieval

Better semantic matching

3️⃣ Embeddings (core idea)

Each chunk is converted into a 384-dimensional vector.

Key rule:

Text with similar meaning → vectors close together

This is why:

“What is deep learning?”

“Explain deep neural networks”

→ retrieve the same content.

4️⃣ Vector storage (Qdrant)

Qdrant stores:

Vector

Metadata (title, source URL)

It does fast cosine similarity search.

5️⃣ Query-time flow

When you ask a question:

Query is embedded

Vector is compared against 12,560 stored vectors

Top-K closest matches returned

Image → text search

Multimodal chat later

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


<img width="768" height="456" alt="image" src="https://github.com/user-attachments/assets/e0be60c5-8426-4437-a9fb-b8c85516aa3d" />

