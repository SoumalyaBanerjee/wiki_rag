# Phase 3 Implementation Guide: Step-by-Step Testing

## Overview

This guide walks you through implementing and testing Phase 3 components step-by-step.

**Components created:**
1. ✅ `requirements.txt` - Updated dependencies
2. ✅ `.env.example` - Configuration template
3. ✅ `scripts/config.py` - Config management
4. ✅ `scripts/utils/citation_manager.py` - Citation tracking
5. ✅ `scripts/utils/retriever.py` - Multimodal search
6. ✅ `scripts/utils/rag_agent.py` - Chat logic (requires LLM API)
7. ✅ `scripts/test_agent.py` - Comprehensive tests

---

## Step 1: Install Dependencies

### What's needed
Update Python packages with Phase 3 requirements (LangChain, Streamlit, LLM providers).

### How to do it

```powershell
# 1. Navigate to project
cd c:\Users\souma\projects\wiki_rag

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install from requirements.txt
pip install -r requirements.txt

# Expected output:
# Successfully installed langchain-0.1.0 langchain-groq-0.0.1 ...
# Collecting packages...
```

### Testing Step 1

**Test 1.1: Verify imports**

```powershell
python -c "import langchain; print(f'LangChain version: {langchain.__version__}')"
# Expected: LangChain version: 0.1.x

python -c "import streamlit; print('Streamlit OK')"
# Expected: Streamlit OK

python -c "import qdrant_client; print('Qdrant client OK')"
# Expected: Qdrant client OK

python -c "import open_clip; print('OpenCLIP OK')"
# Expected: OpenCLIP OK
```

**Test 1.2: List installed packages**

```powershell
pip list | grep -E "langchain|streamlit|groq|openai"
```

Expected output should include:
```
langchain              0.1.x
langchain-community    0.0.x
langchain-groq         0.0.x
streamlit              1.28.x
```

---

## Step 2: Setup Configuration

### What's needed
Create `.env` file with API keys and Qdrant settings.

### How to do it

**2.1: Copy environment template**

```powershell
cp .env.example .env
```

**2.2: Edit `.env` file**

Open `c:\Users\souma\projects\wiki_rag\.env` and set:

```
# Option A: Use Groq (recommended for POC - free)
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here

# Option B: Use OpenAI (requires payment)
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_api_key_here

# Option C: Use Local (requires Ollama installed)
# LLM_PROVIDER=local
# OLLAMA_BASE_URL=http://localhost:11434
```

**Where to get API keys:**

1. **Groq** (Recommended): https://console.groq.com/keys
   - Sign up
   - Create API key
   - Free tier available
   - Copy key to `.env`

2. **OpenAI**: https://platform.openai.com/api-keys
   - Requires credit card
   - ~$0.001 per query

3. **Local**: Install Ollama
   - https://ollama.ai
   - No API keys needed

### Testing Step 2

**Test 2.1: Load configuration**

```powershell
python scripts/config.py
```

Expected output:
```
╔══════════════════════════════════════╗
║   RAG Agent Configuration             ║
╚══════════════════════════════════════╝

LLM Configuration:
  • Provider: groq
  • Max Tokens: 1024
  • Temperature: 0.7
  
[...]

✅ Configuration is valid
```

**Test 2.2: Verify environment variables**

```powershell
python -c "from config import Config; print(f'LLM: {Config.LLM_PROVIDER}'); print(f'Qdrant: {Config.QDRANT_HOST}:{Config.QDRANT_PORT}')"
```

Expected:
```
LLM: groq
Qdrant: localhost:6333
```

---

## Step 3: Test Citation Manager

### What's needed
Verify citation tracking works independently.

### How to do it

**3.1: Run citation test**

```powershell
cd scripts

python -c "
from utils.citation_manager import CitationManager

# Create manager
manager = CitationManager()

# Add citations
manager.add_text_citation('AI', 'https://en.wikipedia.org/wiki/AI', 0.95, 'Artificial Intelligence...')
manager.add_text_citation('ML', 'https://en.wikipedia.org/wiki/ML', 0.88)
manager.add_image_citation('diagram.png', 'minio://wiki-images/diagram.png', 0.85)

# Test output
print(f'✅ Citations added: {manager.count()}')
print('\n📋 Formatted:')
for citation in manager.format_citations():
    print(citation)
"
```

Expected output:
```
✅ Citations added: 3

📋 Formatted:
[1] AI (Score: 0.95)
    https://en.wikipedia.org/wiki/AI
    Snippet: Artificial Intelligence...

[2] ML (Score: 0.88)
    https://en.wikipedia.org/wiki/ML

[3] diagram.png (Score: 0.85)
    minio://wiki-images/diagram.png
```

---

## Step 4: Test Retriever Initialization

### What's needed
Verify retriever can connect to Qdrant and load models.

### How to do it

**4.1: Ensure Docker is running**

```powershell
docker ps
```

Should show:
```
CONTAINER ID   IMAGE                NAMES
abc123...      qdrant/qdrant        qdrant
def456...      minio/minio          minio
```

If not running:
```powershell
docker-compose up -d
```

**4.2: Run retriever test**

```powershell
cd scripts

python -c "
from utils.retriever import Retriever

print('🔹 Initializing retriever...')
retriever = Retriever()

print('\n🔍 Health Check:')
health = retriever.health_check()
for component, status in health.items():
    print(f'  {component}: {status}')
"
```

Expected output:
```
🔹 Initializing retriever...
🔹 Using device: cpu
✅ Connected to Qdrant at localhost:6333
🔹 Loading sentence-transformers model...
✅ Text embedding model loaded
🔹 Loading OpenCLIP model...
✅ OpenCLIP model loaded (ViT-B-32)

🔍 Health Check:
  qdrant: ✅ Online
  text_collection: ✅ Ready
  image_collection: ✅ Ready
  embeddings: ✅ Ready
  clip_model: ✅ Ready
```

**If you see errors:**

```
❌ Connected to Qdrant: Connection refused
```

**Solution:** Docker not running
```powershell
docker-compose up -d
# Wait 10 seconds
python scripts/test_agent.py
```

---

## Step 5: Test Text Retrieval

### What's needed
Verify text search works on Wikipedia data.

### How to do it

**5.1: Test single query**

```powershell
cd scripts

python -c "
from utils.retriever import Retriever

retriever = Retriever()

results = retriever.retrieve_text('What is deep learning?', k=2)

if results:
    for i, result in enumerate(results, 1):
        print(f'\n[{i}] {result[\"title\"]} ({result[\"score\"]:.2f})')
        print(f'    {result[\"text\"][:100]}...')
else:
    print('No results found')
"
```

Expected output:
```
[1] Deep learning (0.92)
    Deep learning is part of a broader family of machine learning methods...

[2] Neural networks (0.88)
    In machine learning, a neural network is a model inspired by biological...
```

**If no results:**
- Check if data was ingested: Run `python scripts/1.ingest_wikipedia.py` first
- Check Qdrant: Visit http://localhost:6333/dashboard

---

## Step 6: Test Image Retrieval

### What's needed
Verify image search works with OpenCLIP embeddings.

### How to do it

**6.1: Test image search**

```powershell
cd scripts

python -c "
from utils.retriever import Retriever

retriever = Retriever()

results = retriever.retrieve_images('neural network diagram', k=2)

if results:
    for i, result in enumerate(results, 1):
        print(f'\n[{i}] {result[\"image_name\"]} ({result[\"score\"]:.2f})')
        print(f'    {result[\"minio_path\"]}')
else:
    print('No images found')
"
```

Expected output:
```
[1] neural_net_1.jpg (0.78)
    minio://wiki-images/neural_net_1.jpg

[2] deep_learning.png (0.75)
    minio://wiki-images/deep_learning.png
```

**If no images:**
- Check if images were ingested: Run `python scripts/4.ingest_images_clip.py` first
- Verify MinIO: Visit http://localhost:9001 (admin/password123)

---

## Step 7: Test Multimodal Retrieval

### What's needed
Verify combined text + image search works.

### How to do it

**7.1: Test multimodal query**

```powershell
cd scripts

python -c "
from utils.retriever import Retriever

retriever = Retriever()

result = retriever.retrieve_multimodal(
    'neural networks and machine learning',
    text_k=2,
    image_k=2
)

print(f'📊 Results: {result[\"total_results\"]} total')
print(f'   • Text: {len(result[\"texts\"])} articles')
print(f'   • Images: {len(result[\"images\"])} images')
"
```

Expected output:
```
📊 Results: 4 total
   • Text: 2 articles
   • Images: 2 images
```

---

## Step 8: Run Comprehensive Test Suite

### What's needed
Run all tests together to verify everything works.

### How to do it

**8.1: Run test_agent.py**

```powershell
cd scripts
python test_agent.py
```

This runs 6 tests in sequence:

```
════════════════════════════════════════════════════════════════════════════════
🧪 PHASE 3 COMPONENT TESTS
════════════════════════════════════════════════════════════════════════════════

============================================================
TEST 1: Configuration
============================================================
[Output of config summary]
✅ Configuration validation passed

============================================================
TEST 2: Citation Manager
============================================================
✅ Added 3 citations (1 duplicate)
✅ Total unique citations: 3
[Citation output]
✅ Citation manager test passed

============================================================
TEST 3: Retriever Initialization
============================================================
[Health check output]
✅ All components healthy

============================================================
TEST 4: Text Retrieval
============================================================
[Text retrieval results for 3 queries]
✅ Text retrieval test passed

============================================================
TEST 5: Image Retrieval
============================================================
[Image retrieval results]
✅ Image retrieval test passed

============================================================
TEST 6: Multimodal Retrieval
============================================================
[Multimodal results]
✅ Multimodal retrieval test passed

════════════════════════════════════════════════════════════════════════════════
📊 TEST SUMMARY
════════════════════════════════════════════════════════════════════════════════
Configuration............................ ✅ PASS
Citation Manager......................... ✅ PASS
Retriever Init........................... ✅ PASS
Text Retrieval........................... ✅ PASS
Image Retrieval.......................... ✅ PASS
Multimodal Retrieval..................... ✅ PASS

Total: 6/6 passed

🎉 All tests passed!
```

---

## Troubleshooting

### "Connection refused" - Qdrant not running

```powershell
docker-compose up -d
docker ps  # verify containers running
```

### "GROQ_API_KEY not set" - Missing API key

```powershell
# Edit .env file
notepad .env

# Set GROQ_API_KEY=your_key_here
```

### Models not loading - Download issue

```powershell
# Force download of models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
python -c "import open_clip; open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')"
```

### "No text results found" - Data not ingested

```powershell
# Ingest Wikipedia articles
python scripts/1.ingest_wikipedia.py

# Ingest images
python scripts/4.ingest_images_clip.py
```

---

## Next Steps

After all tests pass ✅:

1. **Step 9**: Build the RAG Agent class (already created, needs testing)
2. **Step 10**: Build Streamlit UI (`6.streamlit_app.py`)
3. **Step 11**: Create integration test for full chat flow
4. **Step 12**: Commit to git

---

## Quick Reference

**All commands in order:**

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup config
cp .env.example .env
# Edit .env with your API key

# 3. Run tests
cd scripts
python test_agent.py

# 4. If all tests pass ✅, next:
# - Build Streamlit UI
# - Test chat agent
# - Commit changes
```

---

## File Locations Reference

```
scripts/
├── config.py                    ← Configuration loader
├── test_agent.py               ← All tests (run this!)
├── utils/
│   ├── citation_manager.py     ← Citation tracking
│   ├── retriever.py            ← Text/image search
│   └── rag_agent.py            ← Chat logic (next step)
├── 6.streamlit_app.py          ← Web UI (next step)

.env                            ← Your API keys (create from .env.example)
requirements.txt                ← Dependencies
```
