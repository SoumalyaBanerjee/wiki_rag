import os
import torch
import open_clip
from PIL import Image

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct

from minio import Minio

# ---------------- CONFIG ----------------
BUCKET_NAME = "wiki-images"
COLLECTION_NAME = "wiki_image_poc"
IMAGE_DIR = "data/images"
# ---------------------------------------

print("🔹 Loading OpenCLIP model...")

device = "cpu"  # keep cpu for now
model, preprocess, tokenizer = open_clip.create_model_and_transforms(
    model_name="ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)
model = model.to(device)
model.eval()

# Qdrant client
qdrant = QdrantClient(host="localhost", port=6333)

# Create collection if not exists
if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=512,
            distance=Distance.COSINE
        )
    )

# MinIO client
minio_client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="password123",
    secure=False
)

points = []
point_id = 0

print("🔹 Embedding images...")

for img_name in os.listdir(IMAGE_DIR):
    img_path = os.path.join(IMAGE_DIR, img_name)

    image = Image.open(img_path).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_embedding = model.encode_image(image_input)
        image_embedding /= image_embedding.norm(dim=-1, keepdim=True)

    points.append(
        PointStruct(
            id=point_id,
            vector=image_embedding.squeeze().tolist(),
            payload={
                "image_name": img_name,
                "bucket": BUCKET_NAME
            }
        )
    )

    point_id += 1

# Upload to Qdrant
qdrant.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"✅ Indexed {len(points)} images into Qdrant")
