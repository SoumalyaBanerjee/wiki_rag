import torch
import open_clip

from qdrant_client import QdrantClient

# ---------------- CONFIG ----------------
COLLECTION_NAME = "wiki_image_poc"
# ---------------------------------------

print("🔹 Loading OpenCLIP model...")

device = "cpu"
model, _, tokenizer = open_clip.create_model_and_transforms(
    model_name="ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)
model = model.to(device)
model.eval()

qdrant = QdrantClient(host="localhost", port=6333)

query_text = "neural network diagram"

print(f"🔍 Query: {query_text}")

text_tokens = open_clip.tokenize([query_text]).to(device)

with torch.no_grad():
    text_tokens = open_clip.tokenize([query_text]).to(device)
    text_embedding = model.encode_text(text_tokens)
    text_embedding /= text_embedding.norm(dim=-1, keepdim=True)


results = qdrant.search(
    collection_name=COLLECTION_NAME,
    query_vector=text_embedding.squeeze().tolist(),
    limit=3
)

print("\nTop matching images:")
for hit in results:
    print(
        f"Image: {hit.payload['image_name']} | Score: {round(hit.score, 4)}"
    )
