# Phase 3: Chat Agent (Week 5-6)

## Overview
Build a conversational RAG system that:
- Unifies text AND image search in a single chat interface
- Tracks sources and provides citations
- Maintains multi-turn conversation context
- Answers user questions using both Wikipedia content and relevant images

---

## Architecture Overview

```
User Query
    ↓
Chat Interface (Streamlit)
    ↓
LangChain Agent
    ├→ Text Search (Qdrant + wiki_text_poc)
    ├→ Image Search (Qdrant + wiki_image_poc)
    └→ Citation Tracker
    ↓
LLM (local or API)
    ↓
Response + Images + Citations
```

---

## Phase 3 Deliverables

**Main Deliverable**: Interactive chat interface with unified RAG

| Component | Purpose | Status |
|-----------|---------|--------|
| Chat Script (`6.chat_agent.py`) | LangChain agent + conversation logic | ❌ TODO |
| Chat UI (`6.streamlit_app.py`) | Streamlit web interface | ❌ TODO |
| Citation Manager | Track & format sources | ❌ TODO |
| Conversation Memory | Multi-turn context | ❌ TODO |

---

## Detailed Implementation Steps

### Step 1: Setup & Dependencies
**Goal**: Prepare environment for chat agent

**Subtasks**:
- [ ] Add new dependencies to requirements:
  - `langchain>=0.1.0`
  - `langchain-openai` or `langchain-groq` (for LLM)
  - `streamlit>=1.28.0`
  - `streamlit-chat>=0.1.1` (optional, for better UI)
  - `python-dotenv>=1.0.0` (for API keys)

**Files to create/modify**:
- `requirements.txt` - add new packages
- `.env.example` - template for API keys
- `.env` - actual keys (add to .gitignore)

**Expected output**: Clean environment with all dependencies

---

### Step 2: Build Citation Manager
**Goal**: Track and format sources from search results

**File to create**: `scripts/utils/citation_manager.py`

**Functionality**:
```python
class CitationManager:
    def __init__(self):
        self.citations = []
    
    def add_text_citation(self, title, source_url, snippet):
        # Track text sources from Qdrant
        
    def add_image_citation(self, image_name, image_path, score):
        # Track image sources
        
    def format_citations(self):
        # Return formatted citation list
        
    def get_bibliography(self):
        # Return formatted bibliography
        
    def clear(self):
        # Reset for new query
```

**Requirements**:
- Deduplicate sources (same Wikipedia article shouldn't appear twice)
- Format as: `[1] Title (Score: 0.85) - URL`
- Support both text and image citations
- Track relevance scores

**Expected output**: Reusable citation manager class

---

### Step 3: Build Retrieval Functions
**Goal**: Create unified retrieval system

**File to create**: `scripts/utils/retriever.py`

**Functions**:
```python
def retrieve_text_documents(query: str, k: int = 3) -> List[Dict]:
    """
    Search wiki_text_poc collection in Qdrant
    Return: list of dicts with text, score, metadata
    """
    
def retrieve_images(query: str, k: int = 3) -> List[Dict]:
    """
    Search wiki_image_poc collection in Qdrant
    Use OpenCLIP to encode query text
    Return: list of dicts with image_name, score, minio_path
    """
    
def retrieve_multimodal(query: str, text_k: int = 3, image_k: int = 3) -> Dict:
    """
    Call both retrieve functions
    Combine results
    Return: {"texts": [...], "images": [...]}
    """
```

**Requirements**:
- Use same OpenCLIP model for both queries
- Use same embedding model for text
- Handle errors gracefully (Qdrant down, etc)
- Return normalized scores (0-1)

**Expected output**: Unified retrieval module

---

### Step 4: Build LangChain Agent
**Goal**: Create conversational agent with tool integration

**File to create**: `scripts/utils/rag_agent.py`

**Architecture**:
```python
class RAGAgent:
    def __init__(self, api_key: str = None, use_local: bool = False):
        # Initialize LLM (OpenAI, Groq, or local)
        # Initialize retriever
        # Initialize citation manager
        # Initialize conversation memory
        
    def process_query(self, user_query: str) -> Dict:
        """
        Main agent loop:
        1. Embed user query
        2. Retrieve text documents
        3. Retrieve images
        4. Build context from retrieved docs
        5. Call LLM with context
        6. Track citations
        7. Return response + metadata
        """
        
    def get_conversation_history(self) -> List[Dict]:
        # Return formatted conversation
        
    def clear_history(self):
        # Reset conversation
        
    def format_response(self, answer: str, citations: List, images: List) -> Dict:
        # Return formatted response for UI
```

**LLM Integration Options** (choose one):
1. **OpenAI API** (requires API key)
   - `langchain_openai.ChatOpenAI`
   - Cost: ~$0.001 per query
   
2. **Groq API** (free tier available)
   - `langchain_groq.ChatGroq`
   - Fast & free
   - Recommended for POC
   
3. **Local LLM** (requires 4GB+ VRAM)
   - `langchain_community.llms.Ollama`
   - Models: llama2, mistral, neural-chat
   - No cost but slower

**Prompt Template**:
```
You are a helpful Wikipedia expert assistant.
Use the provided context to answer questions accurately.
Always cite your sources using the [1], [2] format.

Context:
{context}

Question: {question}

Answer with citations.
```

**Expected output**: Working agent class with multi-turn support

---

### Step 5: Build Streamlit Chat Interface
**Goal**: Create web UI for chat agent

**File to create**: `scripts/6.streamlit_app.py`

**Features**:
- [x] Chat message history display
- [x] User input textbox
- [x] Streaming response output
- [x] Display retrieved images
- [x] Show citations/sources
- [x] Clear conversation button
- [x] Settings sidebar (LLM choice, top-k, temperature)

**Layout**:
```
┌─────────────────────────────────────┐
│  📚 Wiki RAG Chat Agent             │
├─────────────────────────────────────┤
│ ⚙️ Settings                         │
│   • LLM Model: [Groq v]            │
│   • Top-K Results: [3]             │
│   • Temperature: [0.7]             │
├─────────────────────────────────────┤
│ Chat History:                       │
│ ┌─────────────────────────────────┐ │
│ │ User: What is AI?               │ │
│ │ Agent: AI is...                 │ │
│ │ 📷 [Image 1] [Image 2]          │ │
│ │ Citations: [1] Title (0.95)     │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ [Your question...              ] 🚀 │
│ [Clear Chat]                        │
└─────────────────────────────────────┘
```

**Components**:
```python
def main():
    st.set_page_config(page_title="Wiki RAG Chat", layout="wide")
    st.title("📚 Wiki RAG Chat Agent")
    
    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        llm_choice = st.selectbox("LLM", ["Groq", "OpenAI", "Local"])
        top_k = st.slider("Results per query", 1, 10, 3)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize agent
    agent = RAGAgent(llm_model=llm_choice)
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # User input
    user_query = st.chat_input("Ask me anything about Wikipedia...")
    
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate response
        with st.chat_message("assistant"):
            response = agent.process_query(user_query)
            st.write(response["answer"])
            
            # Display images
            if response["images"]:
                st.subheader("📷 Related Images")
                cols = st.columns(3)
                for idx, img in enumerate(response["images"]):
                    with cols[idx % 3]:
                        st.image(img["path"], caption=img["name"])
            
            # Display citations
            if response["citations"]:
                with st.expander("📋 Sources"):
                    for citation in response["citations"]:
                        st.write(f"• {citation}")
```

**Expected output**: Working web interface accessible at `localhost:8501`

---

### Step 6: Environment & Configuration
**Goal**: Setup configuration management

**File to create**: `scripts/config.py`

**Content**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # groq, openai, local
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Retrieval Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_TEXT = os.getenv("COLLECTION_TEXT", "wiki_text_poc")
COLLECTION_IMAGE = os.getenv("COLLECTION_IMAGE", "wiki_image_poc")

# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CLIP_MODEL = "ViT-B-32"

# Agent Configuration
MAX_TOKENS = 1024
TEMPERATURE = 0.7
TOP_K_RETRIEVAL = 3
```

**File to create**: `.env.example`

**Content**:
```
# LLM Configuration
LLM_PROVIDER=groq
# Get from: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# Optional: OpenAI
# OPENAI_API_KEY=your_openai_key_here

# Optional: Local LLM with Ollama
# OLLAMA_BASE_URL=http://localhost:11434

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Collections
COLLECTION_TEXT=wiki_text_poc
COLLECTION_IMAGE=wiki_image_poc
```

**Expected output**: Clean config management

---

### Step 7: Integration Testing
**Goal**: Verify all components work together

**File to create**: `scripts/test_agent.py`

**Tests**:
```python
def test_retriever():
    # Test text retrieval
    # Test image retrieval
    # Verify scores are normalized
    
def test_citation_manager():
    # Add citations
    # Check deduplication
    # Check formatting
    
def test_agent():
    # Single query
    # Multi-turn conversation
    # Check response format
    # Verify citations are included
    
def test_streaming():
    # Verify streaming output
```

**Expected output**: Passing tests, confidence in system

---

### Step 8: Demo & Documentation
**Goal**: Create runnable demo

**File to create**: `PHASE_3_DEMO.md`

**Content**:
- Quick start guide
- Example queries
- Screenshots
- Troubleshooting
- Configuration options

**Example Queries to Test**:
1. "What is artificial intelligence?"
2. "Tell me about neural networks and show me related images"
3. "Compare machine learning and deep learning"
4. "What are the applications of computer vision?"

**Expected output**: Ready for user testing

---

## File Structure After Phase 3

```
scripts/
├── 1.ingest_wikipedia.py
├── 2.query_test.py
├── 2.b.query2_test.py
├── 3.upload_images_to_minio.py
├── 4.ingest_images_clip.py
├── 4.b.ingest_animal_images.py
├── 5.text_to_image_search.py
├── 5.b.text_to_image_search_animals.py
├── 5.c.display_images.ipynb
├── 6.streamlit_app.py              ← NEW: Chat interface
├── utils/
│   ├── __init__.py
│   ├── citation_manager.py         ← NEW: Citation tracking
│   ├── retriever.py                ← NEW: Unified retrieval
│   └── rag_agent.py                ← NEW: Chat agent logic
├── config.py                        ← NEW: Configuration
├── test_agent.py                    ← NEW: Integration tests
└── requirements.txt                 ← UPDATED: New dependencies

.env.example                         ← NEW: Configuration template
PHASE_3_DEMO.md                      ← NEW: Demo documentation
```

---

## Dependencies to Add

```
# LLM/Embedding
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-groq>=0.0.1
langchain-community>=0.0.10
openai>=1.0.0

# Vector DB (already have)
qdrant-client>=2.4.0

# UI
streamlit>=1.28.0
streamlit-chat>=0.1.1

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

## Success Criteria

- [ ] Chat agent responds to queries with context-aware answers
- [ ] Citations are accurate and properly formatted
- [ ] Images are retrieved and displayed for multimodal queries
- [ ] Conversation history is maintained (multi-turn)
- [ ] Streamlit UI is responsive and user-friendly
- [ ] No API errors in logs
- [ ] Response time < 5 seconds per query
- [ ] Works with at least 2 LLM options

---

## Estimated Timeline

| Step | Task | Hours |
|------|------|-------|
| 1 | Setup & Dependencies | 0.5 |
| 2 | Citation Manager | 1 |
| 3 | Retrieval Functions | 1.5 |
| 4 | LangChain Agent | 3 |
| 5 | Streamlit UI | 2 |
| 6 | Configuration | 0.5 |
| 7 | Testing | 2 |
| 8 | Demo & Docs | 1 |
| **Total** | | **11.5 hours** |

---

## Decision Points

**1. Which LLM to use?**
- **Groq** (Recommended): Fast, free tier, no setup
- **OpenAI**: Most capable but costs money
- **Local**: No cost but needs hardware

**2. Conversation Memory Strategy**
- **Simple**: Store in Streamlit session state (works locally)
- **Advanced**: Use LangChain's ConversationBufferMemory
- **Production**: Use database backend

**3. Citation Format**
- **Simple**: "[1] Title - URL"
- **Rich**: "[1] Title (0.95) - URL - Snippet"
- **APA**: Full APA citation format

---

## Next Steps

1. **Start with Step 1**: Add dependencies to `requirements.txt`
2. **Then Step 2**: Build `citation_manager.py`
3. **Then Step 3**: Build `retriever.py`
4. **Continue in order** to keep dependencies clear

**Recommended approach**: Complete steps 1-4 before creating the UI (step 5).

---

## Notes

- Use the existing Qdrant collections (`wiki_text_poc`, `wiki_image_poc`)
- Reuse embedding models from phases 1-2
- Keep agent logic separate from UI for reusability
- Add comprehensive logging for debugging
- Test each step before moving to the next
