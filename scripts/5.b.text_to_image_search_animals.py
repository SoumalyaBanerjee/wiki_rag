import torch
import open_clip
from qdrant_client import QdrantClient

# -----------------------------
# Load CLIP model
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, _ = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)

tokenizer = open_clip.get_tokenizer("ViT-B-32")

model = model.to(device)
model.eval()

print(f"🔹 Using device: {device}")

# -----------------------------
# Connect to Qdrant
# -----------------------------
qdrant = QdrantClient(host="localhost", port=6333)

# -----------------------------
# Query
# -----------------------------
query = "stripped animal"

print(f"\n🔍 Query: {query}")

# Encode text
text_tokens = tokenizer([query]).to(device)

with torch.no_grad():
    text_embedding = model.encode_text(text_tokens)

    # IMPORTANT — normalize
    text_embedding = text_embedding / text_embedding.norm(dim=-1, keepdim=True)

text_embedding = text_embedding.cpu().numpy()[0]

# -----------------------------
# Search
# -----------------------------
results = qdrant.search(
    collection_name="demo_animals",
    query_vector=text_embedding.tolist(),
    limit=5,
)

# -----------------------------
# Display results
# -----------------------------
print("\nTop matches:")

for r in results:
    print(f"Image: {r.payload['image_name']} | Score: {r.score:.4f}")
