# wiki_rag

Start with :

Start the docker in local system

cd c:\Users\souma\projects\wiki_rag
.\.venv\Scripts\streamlit run scripts/6.streamlit_app.py

A small research/experiment repository for retrieval-augmented generation (RAG) using Qdrant, MinIO, and local image/text ingestion scripts.

---

## 🎯 Project Overview: Completed Phases

### Phase 1 ✅ Setup & POC (Week 1-2) — COMPLETE

**Objective**: Build foundational infrastructure for text-based RAG using Wikipedia.

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: TEXT RAG                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Wikipedia Data Source                                          │
│  ↓                                                              │
│  [1.ingest_wikipedia.py]                                       │
│  • Fetch ~100 Wikipedia articles (10 topics × 10 each)        │
│  • Topics: AI, ML, DL, NN, CV, NLP, Data Science, etc        │
│                                                                  │
│  Data Processing                                                │
│  ↓                                                              │
│  [Text Chunking & Embedding]                                   │
│  • RecursiveCharacterTextSplitter                             │
│    - Chunk size: 500 tokens                                    │
│    - Overlap: 100 tokens                                       │
│  • Embedding Model: sentence-transformers/all-MiniLM-L6-v2   │
│    - Vector dimension: 384                                     │
│    - Fast & lightweight (~22M params)                          │
│                                                                  │
│  Vector Storage                                                 │
│  ↓                                                              │
│  [Qdrant Vector Database] 🐳 (Docker Container)               │
│  • Collection: wiki_text_poc                                   │
│  • Total vectors: ~12,560 (100 articles × avg 125 chunks)    │
│  • Distance metric: Cosine similarity                          │
│  • Metadata stored: {title, source_url, chunk_text}          │
│                                                                  │
│  Query Interface                                               │
│  ↓                                                              │
│  [2.query_test.py & 2.b.query2_test.py]                      │
│  • User query → embed → cosine similarity search              │
│  • Return top-k similar chunks                                │
│  • Display metadata (source, URL)                             │
│                                                                  │
│  Success Metrics                                               │
│  ✅ 12,560+ vectors stored and searchable                    │
│  ✅ Sub-second query response time                            │
│  ✅ Accurate semantic matching                                │
└─────────────────────────────────────────────────────────────────┘
```

#### Technical Details: Phase 1

| Component | Technology | Configuration | Purpose |
|-----------|-----------|----------------|---------|
| **Data Source** | Wikipedia API | 100 articles | Training corpus |
| **Text Splitting** | LangChain RecursiveCharacterTextSplitter | 500 tokens, 100 overlap | Optimal chunk size for embeddings |
| **Embedding Model** | sentence-transformers/all-MiniLM-L6-v2 | 384-dim vectors | Fast, lightweight embeddings |
| **Vector DB** | Qdrant | Docker on port 6333 | HNSW index, cosine distance |
| **Storage** | `qdrant_storage/` volume | Persistent | Survives container restarts |
| **Query Engine** | LangChain QdrantVectorStore | similarity_search(k=3) | Semantic search |

#### Data Flow Example

```
User Query: "What is deep learning?"
        ↓
   [Embedding Layer]
   • Tokenize & encode query
   • Output: 384-dim vector
        ↓
   [Similarity Search]
   • Compare against 12,560 stored vectors
   • Calculate cosine similarity
   • Rank by score
        ↓
   [Results]
   Top 3 matches:
   1. Score: 0.92 | Title: "Deep Learning" | Source: wikipedia.org/wiki/Deep_learning
   2. Score: 0.88 | Title: "Neural Networks" | Source: wikipedia.org/wiki/Artificial_neural_network
   3. Score: 0.85 | Title: "Machine Learning" | Source: wikipedia.org/wiki/Machine_learning
```

#### Scripts in Phase 1

- **`1.ingest_wikipedia.py`** (67 lines)
  - Fetches Wikipedia articles using `wikipedia` library
  - Splits text using `RecursiveCharacterTextSplitter`
  - Generates embeddings with sentence-transformers
  - Uploads to Qdrant via `Qdrant.from_texts()`

- **`2.query_test.py`** (22 lines)
  - Loads embeddings + Qdrant client
  - Performs similarity search with `vector_store.similarity_search(query, k=3)`
  - Prints results with source metadata

- **`2.b.query2_test.py`** (Similar variant)
  - Alternative query implementation

---

### Phase 2 ✅ Multimodal Indexing (Week 3-4) — COMPLETE

**Objective**: Extend RAG to support image search using multimodal embeddings (CLIP).

#### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│              PHASE 2: TEXT + IMAGE MULTIMODAL RAG               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐      ┌──────────────────────┐          │
│  │ TEXT TRACK          │      │ IMAGE TRACK          │          │
│  ├─────────────────────┤      ├──────────────────────┤          │
│  │ (From Phase 1)      │      │ (NEW in Phase 2)     │          │
│  │                     │      │                      │          │
│  │ wiki_text_poc       │      │ Image Files          │          │
│  │ Collection          │      │ data/images/         │          │
│  │ 12,560 vectors      │      │ 150+ demo images     │          │
│  │ 384-dim             │      │                      │          │
│  │                     │      │ ↓                    │          │
│  │ Embedding Model:    │      │ [3.upload_images    │          │
│  │ sentence-trans      │      │  _to_minio.py]      │          │
│  │ all-MiniLM-L6-v2    │      │ • Upload to MinIO    │          │
│  │                     │      │ • S3-compatible      │          │
│  │                     │      │ • Bucket: wiki-images           │
│  │                     │      │                      │          │
│  │                     │      │ ↓                    │          │
│  │                     │      │ [4.ingest_images    │          │
│  │                     │      │  _clip.py]          │          │
│  │                     │      │ • Load OpenCLIP      │          │
│  │                     │      │   model (ViT-B-32)  │          │
│  │                     │      │ • Encode each image │          │
│  │                     │      │ • Extract 512-dim   │          │
│  │                     │      │   image vectors     │          │
│  │                     │      │                      │          │
│  │                     │      │ wiki_image_poc       │          │
│  │                     │      │ Collection           │          │
│  │                     │      │ 150+ vectors         │          │
│  │                     │      │ 512-dim              │          │
│  └─────────────────────┘      └──────────────────────┘          │
│         ↓                                ↓                        │
│    [Qdrant Vector Database - Docker Container]                  │
│    • 2 Collections                                               │
│    • 12,560 text vectors (384-dim)                             │
│    • 150+ image vectors (512-dim)                              │
│    • Both indexed with HNSW                                    │
│         ↓                                ↓                        │
│    [Query Interface]                                            │
│    • Text query: embed with sentence-transformers              │
│    • Image query: embed with OpenCLIP                          │
│    • Text→Image search: "neural network" → related images     │
│         ↓                                ↓                        │
│  [5.text_to_image_search.py]  [5.b.text_to_image_search_animals.py]
│  • Embed text query with OpenCLIP                              │
│  • Search wiki_image_poc by similarity                         │
│  • Return top-3 matching images with scores                   │
│                                                                   │
│  Success Metrics                                                 │
│  ✅ Text + Image indices operational                           │
│  ✅ Cross-modal search working (text→images)                  │
│  ✅ MinIO object storage configured                           │
│  ✅ Demo notebook created (5.c.display_images.ipynb)         │
└──────────────────────────────────────────────────────────────────┘
```

#### Technical Details: Phase 2

| Component | Technology | Configuration | Purpose |
|-----------|-----------|----------------|---------|
| **Image Storage** | MinIO | Docker on port 9000 | S3-compatible object storage |
| **Image Embedding** | OpenCLIP (ViT-B-32) | 512-dim vectors | Vision-language model |
| **Pretraining** | LAION-2B | laion2b_s34b_b79k | 2B image-text pairs |
| **Image Collection** | Qdrant wiki_image_poc | HNSW index | Fast image retrieval |
| **Query Embedding** | OpenCLIP tokenizer | Text→image vector | Cross-modal search |
| **Search Type** | Cosine similarity | k=3 neighbors | Top matching images |

#### Multimodal Data Flow Example

```
User Query: "Show me images of neural networks"
        ↓
   [OpenCLIP Encoder]
   • Tokenize text query
   • Pass through ViT-B-32 image encoder head
   • Output: 512-dim vector
        ↓
   [Image Similarity Search]
   • Compare against 150 stored image vectors
   • Calculate cosine similarity
   • Rank by score
        ↓
   [Results]
   Top 3 matching images:
   1. Score: 0.78 | Image: neural_network_diagram.png
   2. Score: 0.75 | Image: deep_learning_architecture.jpg
   3. Score: 0.72 | Image: cnn_architecture.png
        ↓
   [MinIO Retrieval]
   • Fetch images from wiki-images bucket
   • Return to user with metadata
```

#### Scripts in Phase 2

- **`3.upload_images_to_minio.py`** (20 lines)
  - Connects to MinIO (S3-compatible)
  - Uploads all images from `data/images/` to `wiki-images` bucket
  - Handles bucket creation if needed

- **`4.ingest_images_clip.py`** (84 lines)
  - Loads OpenCLIP model (ViT-B-32, LAION2B pretrained)
  - Iterates through `data/images/`
  - Encodes each image to 512-dim vector
  - Stores in Qdrant `wiki_image_poc` collection with metadata

- **`4.b.ingest_animal_images.py`** (Variant)
  - Same logic as `4.ingest_images_clip.py`
  - Specialized for animal images dataset

- **`5.text_to_image_search.py`** (42 lines)
  - Embeds user text query with OpenCLIP
  - Searches `wiki_image_poc` collection
  - Displays top-3 matching images with scores

- **`5.b.text_to_image_search_animals.py`** (Variant)
  - Same logic, specialized for animal images

- **`5.c.display_images.ipynb`** (Jupyter Notebook)
  - Interactive demo with visualizations
  - Allows testing multiple queries
  - Displays results in notebook format

---

### Key Achievements Summary

#### Phase 1 Achievements
- ✅ **Infrastructure**: Qdrant + Docker setup
- ✅ **Data Pipeline**: Wikipedia → chunks → embeddings → vectors
- ✅ **Search Capability**: Semantic similarity search on text
- ✅ **Scale**: 12,560+ indexed vectors
- ✅ **Performance**: Sub-second queries

#### Phase 2 Achievements
- ✅ **Multimodal Support**: Added image embeddings
- ✅ **Vision-Language Model**: OpenCLIP integration
- ✅ **Object Storage**: MinIO for image files
- ✅ **Cross-Modal Search**: Text queries find images
- ✅ **Dual Collection**: Separate indices for text/images
- ✅ **Demo Coverage**: Multiple use cases tested

#### Combined System Capabilities
- Search Wikipedia articles by semantic meaning
- Find images relevant to text queries
- Demo-ready scripts for all core operations
- Docker-based infrastructure (reproducible)
- S3-compatible storage for scalability

---

## Project structure

- `docker-compose.yml` — launches Qdrant and MinIO services used by the scripts.
- `data/` — datasets and images used for demos (not recommended to commit large files to Git).
- `minio_data/`, `qdrant_storage/` — local storage used by containers (should be ignored from git).
- `scripts/` — python scripts for ingestion, querying, and demos:
  - `1.ingest_wikipedia.py` — ingest Wikipedia text (overview).
  - `2.query_test.py`, `2.b.query2_test.py` — query examples.
  - `3.upload_images_to_minio.py` — upload images to MinIO.
  - `4.ingest_images_clip.py`, `4.b.ingest_animal_images.py` — image ingestion and embeddings.
  - `5.text_to_image_search.py`, `5.b.text_to_image_search_animals.py`, `5.c.display_images.ipynb` — search & display demos.

## Prerequisites

- Windows 10/11 up to date
- Docker Desktop (with WSL2 recommended)
- Python 3.10+
- VS Code (recommended extensions: Python)
- (Optional) Git

## Quick setup (PowerShell)

Open PowerShell and run:

```powershell
# create venv & activate
python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install --upgrade pip

# install common requirements used by the scripts
pip install langchain sentence-transformers qdrant-client wikipedia tqdm requests open-clip-torch pillow boto3 minio

# start services
docker-compose up -d
```

Note: the project contains a `docker-compose.yml` that will start `qdrant` and `minio` (ports 6333 and 9000/9001).

## Running the demos

1. Start Docker services: `docker-compose up -d`.
2. Ensure Python environment is activated and dependencies installed.
3. Run ingestion scripts in order (for text/images) then run query/search scripts in `scripts/`.

## Configuration

- MinIO default credentials (from `docker-compose.yml`):
  - user: `admin`
  - password: `password123`
- Qdrant runs on `http://localhost:6333` by default.

## Notes

- This repo includes example demo images under `data/`. For a Git repository you may want to remove or move large binary assets and use an external storage or Git LFS.
- I added a `.gitignore` to avoid committing virtual environments and container storage directories.

## Contributing

Open an issue or pull request with changes.

## License

Add a license file if you plan to publish this repository publicly.
