import os
import torch
import open_clip
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# -----------------------------
# Load CLIP model
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)

model = model.to(device)
model.eval()

print(f"🔹 Using device: {device}")

# -----------------------------
# Connect Qdrant
# -----------------------------
qdrant = QdrantClient(host="localhost", port=6333)
collection = "demo_animals"

# Recreate collection cleanly
qdrant.recreate_collection(
    collection_name=collection,
    vectors_config=VectorParams(size=512, distance=Distance.COSINE),
)

print("✅ Qdrant collection ready")

# -----------------------------
# Image directory (FIXED PATH)
# -----------------------------
image_dir = r"data\demo_images"

points = []

# -----------------------------
# Encode images
# -----------------------------
for idx, img_name in enumerate(os.listdir(image_dir)):
    img_path = os.path.join(image_dir, img_name)

    try:
        image = preprocess(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)

        with torch.no_grad():
            embedding = model.encode_image(image)

            # IMPORTANT — normalize
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)

        embedding = embedding.cpu().numpy()[0]

        points.append(
            PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload={
                    "image_name": img_name,
                    "label": os.path.splitext(img_name)[0],
                    "source": img_path
                },
            )
        )

        print(f"✅ Encoded {img_name}")

    except Exception as e:
        print(f"⚠️ Failed {img_name}: {e}")

# -----------------------------
# Upload to Qdrant
# -----------------------------
qdrant.upsert(collection_name=collection, points=points)

print(f"\n🚀 Uploaded {len(points)} images to Qdrant")
