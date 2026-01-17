import torch
import open_clip
from qdrant_client import QdrantClient

# Load CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, _ = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k"
)
tokenizer = open_clip.get_tokenizer("ViT-B-32")
model = model.to(device)
model.eval()

# Qdrant
qdrant = QdrantClient(host="localhost", port=6333)

query = "PT"

text_tokens = tokenizer([query]).to(device)
with torch.no_grad():
    text_embedding = model.encode_text(text_tokens).cpu().numpy()[0]

results = qdrant.search(
    collection_name="demo_animals",
    query_vector=text_embedding.tolist(),
    limit=3,
)

print(f"\n🔍 Query: {query}")
for r in results:
    print(f"Image: {r.payload['image_name']} | Score: {r.score:.3f}")
