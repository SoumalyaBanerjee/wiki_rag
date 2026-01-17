# wiki_rag

A small research/experiment repository for retrieval-augmented generation (RAG) using Qdrant, MinIO, and local image/text ingestion scripts.

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
