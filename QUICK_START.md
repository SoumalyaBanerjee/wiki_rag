# Phase 3 Quick Start - Copy & Paste Commands

## Prerequisites
- Docker running: `docker-compose up -d`
- Python 3.10+ active

## Quick Setup (5 minutes)

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your API key
# Open .env and set:
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_key_from_https://console.groq.com/keys
```

## Run All Tests (2 minutes)

```powershell
cd scripts
python test_agent.py

# Expected: 6/6 tests passed ✅
```

## Test Individual Components

### Test Configuration
```powershell
cd scripts
python config.py
```

### Test Citation Manager
```powershell
cd scripts
python -c "
from utils.citation_manager import CitationManager
m = CitationManager()
m.add_text_citation('Test', 'url', 0.95)
print(m.format_citations())
"
```

### Test Retriever
```powershell
cd scripts
python -c "
from utils.retriever import Retriever
r = Retriever()
print(r.health_check())
"
```

### Test Text Search
```powershell
cd scripts
python -c "
from utils.retriever import Retriever
r = Retriever()
results = r.retrieve_text('artificial intelligence', k=2)
for r in results:
    print(f'{r[\"title\"]}: {r[\"score\"]:.2f}')
"
```

### Test Image Search
```powershell
cd scripts
python -c "
from utils.retriever import Retriever
r = Retriever()
results = r.retrieve_images('neural network diagram', k=2)
for r in results:
    print(f'{r[\"image_name\"]}: {r[\"score\"]:.2f}')
"
```

### Test Multimodal
```powershell
cd scripts
python -c "
from utils.retriever import Retriever
r = Retriever()
results = r.retrieve_multimodal('machine learning')
print(f'Texts: {len(results[\"texts\"])}, Images: {len(results[\"images\"])}')
"
```

## Troubleshooting Quick Fixes

### Docker not running
```powershell
docker-compose up -d
```

### API key error
```powershell
# Edit .env
notepad .env
# Add: GROQ_API_KEY=your_key_here
```

### Module not found
```powershell
pip install -r requirements.txt
```

### Qdrant/MinIO not working
```powershell
# Check health
python scripts/test_agent.py

# Or manually check
curl http://localhost:6333/health
```

## Files Created

```
✅ requirements.txt              (Dependencies)
✅ .env.example                  (Config template)
✅ scripts/config.py             (Configuration)
✅ scripts/utils/citation_manager.py  (Citations)
✅ scripts/utils/retriever.py    (Search engine)
✅ scripts/utils/rag_agent.py    (Chat logic)
✅ scripts/test_agent.py         (All tests)
✅ PHASE_3_TESTING_GUIDE.md      (Detailed guide)
✅ PHASE_3_PROGRESS.md           (What was done)
```

## Full Documentation

For detailed testing steps, see: `PHASE_3_TESTING_GUIDE.md`
For overview of what was done, see: `PHASE_3_PROGRESS.md`

## Import Examples

```python
# Configuration
from config import Config
print(Config.LLM_PROVIDER)
Config.validate()

# Citation tracking
from utils.citation_manager import CitationManager
manager = CitationManager()

# Search engine
from utils.retriever import Retriever
retriever = Retriever()
texts = retriever.retrieve_text("query")
images = retriever.retrieve_images("query")

# Chat agent
from utils.rag_agent import RAGAgent
agent = RAGAgent()
response = agent.process_query("What is AI?")
```

## Next Step

After tests pass ✅:
- Build Streamlit UI: `scripts/6.streamlit_app.py`
- Run: `streamlit run scripts/6.streamlit_app.py`
