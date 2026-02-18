from multimodal_rag import MultimodalRAG
from PIL import Image
import os

rag = MultimodalRAG()

query = input("\n🔍 Enter query: ")

# ---- call RAG ----
answer, images, docs = rag.answer(query)

print("\n================ ANSWER ================\n")
print(answer)

# -------- TEXT CITATIONS --------
print("\n================ TEXT SOURCES ================\n")

for i, doc in enumerate(docs, 1):
    title = doc.metadata.get("title", "Unknown")
    source = doc.metadata.get("source", "Unknown")

    print(f"[{i}] {title}")
    print(f"Source: {source}")
    print(f"Snippet: {doc.page_content[:250]}...")
    print("-" * 60)

# -------- IMAGE RESULTS --------
IMAGE_DIR = "data/demo_images"

print("\n================ IMAGES ================\n")

for r in images:
    img_name = r.payload.get("image_name")
    score = r.score

    print(f"{img_name} | Score: {score:.3f}")

    img_path = os.path.join(IMAGE_DIR, img_name)

    try:
        Image.open(img_path).show()
    except:
        print("⚠️ Could not open image")
