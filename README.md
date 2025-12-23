🧩 PHASE 1 — TEXT RAG (RECAP DIAGRAM)


┌────────────────────┐
│  Wikipedia Pages   │
│  (~100 articles)   │
└─────────┬──────────┘
          │
          │ 1. Fetch content (wikipedia API)
          ▼
┌────────────────────┐
│  Raw Text Content  │
│  (long articles)  │
└─────────┬──────────┘
          │
          │ 2. Chunking
          │    (RecursiveCharacterTextSplitter)
          ▼
┌────────────────────┐
│  Text Chunks       │
│  (~12,500 chunks) │
└─────────┬──────────┘
          │
          │ 3. Embeddings
          │    (Sentence Transformers)
          ▼
┌────────────────────────────────┐
│  Vector Embeddings (384-dim)   │
│  all-MiniLM-L6-v2              │
└─────────┬──────────────────────┘
          │
          │ 4. Store vectors + metadata
          ▼
┌────────────────────────────────┐
│  QDRANT Vector Database        │
│  - embedding                  │
│  - title                      │
│  - source (URL)               │
└─────────┬──────────────────────┘
          │
          │ 5. User Query
          ▼
┌────────────────────┐
│  User Question     │
│ "What is DL?"      │
└─────────┬──────────┘
          │
          │ 6. Query embedding
          ▼
┌────────────────────────────────┐
│  Query Vector                  │
│  (same embedding model)        │
└─────────┬──────────────────────┘
          │
          │ 7. Similarity Search
          ▼
┌────────────────────────────────┐
│  Top-K Chunks                  │
│  (semantic matches)            │
└─────────┬──────────────────────┘
          │
          │ 8. Output
          ▼
┌────────────────────────────────┐
│  Retrieved Text + Sources      │
│  (Wikipedia links)             │
└────────────────────────────────┘

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


🎯 PHASE 1 — WHAT YOU ACHIEVED (IMPORTANT)

You now understand and built:

✅ RAG fundamentals
✅ Vector databases
✅ Chunking strategy
✅ Embedding models
✅ Semantic retrieval
✅ Source attribution

This is exactly the same foundation used by:

ChatGPT Retrieval

Perplexity-style search

Internal enterprise RAG systems

🔮 HOW PHASE 2 BUILDS ON THIS

Phase 2 will reuse everything above and add:

Text Embeddings  ─┐
                  ├──► Unified Vector Space (CLIP)
Image Embeddings ─┘


Meaning:

Text → image search

Image → text search

Multimodal chat later
