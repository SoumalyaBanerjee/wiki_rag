import os
import torch
import open_clip
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Load CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k"
)
model = model.to(device)
model.eval()

# Qdrant
qdrant = QdrantClient(host="localhost", port=6333)
collection = "demo_animals"

# Create collection if not exists
qdrant.recreate_collection(
    collection_name=collection,
    vectors_config={"size": 512, "distance": "Cosine"},
)

points = []
image_dir = "data\demo_images"

for idx, img_name in enumerate(os.listdir(image_dir)):
    img_path = os.path.join(image_dir, img_name)

    image = preprocess(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image).cpu().numpy()[0]

    points.append(
        PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                "image_name": img_name,
                "label": img_name.split(".")[0],  # tiger, dog, etc.
            },
        )
    )

qdrant.upsert(collection_name=collection, points=points)

print("✅ Animal images ingested")
