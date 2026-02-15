"""
Streamlit UI for Wiki RAG Chat Agent
====================================

Interactive web interface for the Phase 3 chat agent with:
- Multi-turn conversation
- Real-time Wikipedia + image search
- Citation tracking and source attribution
- Settings configuration
- Conversation history management
"""

from dotenv import load_dotenv


import streamlit as st
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from utils.rag_agent import RAGAgent
from utils.retriever import Retriever
from utils.citation_manager import CitationManager

from langchain_groq import ChatGroq
import os
load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama3-70b-8192",
    temperature=0
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Wiki RAG Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .source-box {
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .citation-badge {
        background-color: #e8f0ff;
        border: 1px solid #1f77b4;
        border-radius: 0.25rem;
        padding: 0.25rem 0.5rem;
        margin-right: 0.25rem;
        font-size: 0.85rem;
    }
    .message-user {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .message-assistant {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "config" not in st.session_state:
        st.session_state.config = Config()
    
    if "agent" not in st.session_state:
        with st.spinner("🔧 Initializing RAG Agent..."):
            try:
                # st.session_state.agent = RAGAgent(st.session_state.config)
                # st.session_state.agent = RAGAgent(
                #                         config=st.session_state.config,
                #                         llm=llm
                #                                 )
                st.session_state.agent = RAGAgent()
                st.session_state.agent_ready = True
            except Exception as e:
                st.session_state.agent_ready = False
                st.session_state.agent_error = str(e)
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "citations" not in st.session_state:
        st.session_state.citations = CitationManager()
    
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False
    
    if "search_results" not in st.session_state:
        st.session_state.search_results = {"text": [], "images": []}

initialize_session_state()

# ============================================================================
# SIDEBAR - CONFIGURATION & CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings & Configuration")
    
    # Agent Status
    if st.session_state.agent_ready:
        st.success("✅ Agent Ready")
    else:
        st.error(f"❌ Agent Error: {st.session_state.agent_error}")
    
    st.divider()
    
    # LLM Provider Selection
    st.markdown("**LLM Configuration**")
    llm_provider = st.selectbox(
        "LLM Provider",
        ["groq", "openai", "ollama"],
        index=0 if st.session_state.config.llm_provider == "groq" else 
              (1 if st.session_state.config.llm_provider == "openai" else 2),
        help="Select which LLM provider to use"
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.config.temperature,
        step=0.1,
        help="Higher = more creative, Lower = more deterministic"
    )
    
    # Max tokens slider
    max_tokens = st.slider(
        "Max Tokens",
        min_value=256,
        max_value=4096,
        value=st.session_state.config.max_tokens,
        step=256,
        help="Maximum length of generated response"
    )
    
    st.divider()
    
    # Retrieval Settings
    st.markdown("**Retrieval Settings**")
    
    enable_text_search = st.checkbox(
        "📄 Text Search",
        value=True,
        help="Search Wikipedia articles"
    )
    
    enable_image_search = st.checkbox(
        "🖼️ Image Search",
        value=True,
        help="Search for relevant images"
    )
    
    top_k = st.slider(
        "Results per Search",
        min_value=1,
        max_value=10,
        value=st.session_state.config.top_k,
        step=1,
        help="Number of results to retrieve"
    )
    
    st.divider()
    
    # Conversation Management
    st.markdown("**Conversation Management**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.citations.clear()
            st.session_state.search_results = {"text": [], "images": []}
            st.rerun()
    
    with col2:
        if st.button("📋 Show Raw History", use_container_width=True):
            st.session_state.show_history = not st.session_state.get("show_history", False)
    
    st.divider()
    
    # Configuration Summary
    with st.expander("📊 Configuration Summary"):
        st.json({
            "llm_provider": st.session_state.config.llm_provider,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_k": top_k,
            "qdrant_host": st.session_state.config.qdrant_host,
            "text_collection": st.session_state.config.text_collection,
            "image_collection": st.session_state.config.image_collection
        })
    
    # About
    st.divider()
    st.markdown("""
        ### 📚 Wiki RAG
        
        **Phase 3: Chat Agent**
        
        An intelligent search and retrieval system combining:
        - 🤖 Large Language Models (Groq, OpenAI, Ollama)
        - 📊 Vector Embeddings (sentence-transformers)
        - 🖼️ Vision Models (OpenCLIP)
        - 🗄️ Vector Database (Qdrant)
        
        **Capabilities:**
        - Multi-turn conversations
        - Text + image search
        - Citation tracking
        - Source attribution
    """)

# ============================================================================
# MAIN CONTENT - CHAT INTERFACE
# ============================================================================

st.markdown('<div class="main-header">🤖 Wiki RAG Chat</div>', unsafe_allow_html=True)
st.markdown("Ask questions about Wikipedia articles and images")

# Agent Status Alert
if not st.session_state.agent_ready:
    st.error(f"⚠️ Agent initialization failed: {st.session_state.agent_error}")
    st.info("Please check your configuration and try refreshing the page.")
else:
    # Conversation Display
    st.markdown("### 💬 Conversation")
    
    conversation_container = st.container()
    with conversation_container:
        if st.session_state.conversation_history:
            for message in st.session_state.conversation_history:
                if message["role"] == "user":
                    st.markdown(
                        f'<div class="message-user"><strong>You:</strong><br>{message["content"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="message-assistant"><strong>Assistant:</strong><br>{message["content"]}</div>',
                        unsafe_allow_html=True
                    )
        else:
            st.info("👋 Start a conversation by asking a question below!")
    
    st.divider()
    
    # Citation & Image Results Display
    if st.session_state.conversation_history:
        col_left, col_right = st.columns([1, 1])
        
        # Citations
        with col_left:
            st.markdown("### 📚 Sources & Citations")
            if st.session_state.citations.citations:
                for citation in st.session_state.citations.citations:
                    with st.container():
                        st.markdown(f"**[{citation.idx}] {citation.title}**")
                        st.markdown(f"*Score: {citation.score:.2f}*")
                        if citation.url:
                            st.markdown(f"🔗 [{citation.url}]({citation.url})")
                        if citation.snippet:
                            st.caption(f"📝 {citation.snippet[:100]}...")
                        st.divider()
            else:
                st.info("No citations yet. Keep asking!")
        
        # Images
        with col_right:
            st.markdown("### 🖼️ Retrieved Images")
            if st.session_state.search_results.get("images"):
                for idx, img_result in enumerate(st.session_state.search_results["images"], 1):
                    try:
                        if "image_path" in img_result:
                            st.image(
                                img_result["image_path"],
                                caption=f"Image {idx} (Score: {img_result.get('score', 0):.2f})",
                                use_column_width=True
                            )
                    except Exception as e:
                        st.warning(f"Could not load image: {e}")
            else:
                st.info("No images retrieved yet. Ask questions about images!")
    
    st.divider()
    
    # Input Section
    st.markdown("### 🔍 Ask a Question")
    
    col_input, col_submit = st.columns([0.85, 0.15])
    
    with col_input:
        user_input = st.text_input(
            "Your question:",
            placeholder="e.g., What is machine learning and show me diagrams?",
            label_visibility="collapsed"
        )
    
    with col_submit:
        submit_button = st.button("Send", use_container_width=True, key="submit_button")
    
    # Process user input
    if submit_button and user_input.strip():
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        with st.spinner("🤔 Thinking..."):
            try:
                # Process query through RAG agent
                response = st.session_state.agent.process_query(user_input)
                
                # Add assistant response to history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Update citations from agent
                if hasattr(st.session_state.agent, 'citations'):
                    st.session_state.citations = st.session_state.agent.citations
                
                # Rerun to display updated conversation
                st.rerun()
                
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
                # Remove the user message if processing failed
                st.session_state.conversation_history.pop()
    
    # Display raw history if requested
    if st.session_state.get("show_history", False):
        with st.expander("📋 Raw Conversation History"):
            for i, msg in enumerate(st.session_state.conversation_history):
                st.json({
                    "index": i,
                    "role": msg["role"],
                    "content": msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                })

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
    <p>Wiki RAG Chat • Phase 3 Implementation</p>
    <p>Powered by LangChain, Qdrant, and OpenCLIP</p>
    </div>
""", unsafe_allow_html=True)
