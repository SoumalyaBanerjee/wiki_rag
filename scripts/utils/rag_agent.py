"""RAG Agent using LangChain with conversation memory."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from utils.retriever import Retriever
from utils.citation_manager import CitationManager
from config import Config


class RAGAgent:
    """
    Conversational RAG agent with multimodal search.
    
    Features:
    - Multi-turn conversation with memory
    - Text and image retrieval
    - Automatic citation tracking
    - Multiple LLM provider support
    - Streaming response support
    """
    
    def __init__(
        self,
        llm_provider: Optional[str] = None,
        enable_memory: bool = True,
        memory_window: int = 5
    ):
        """
        Initialize RAG agent.
        
        Args:
            llm_provider: Override LLM provider (groq, openai, local)
            enable_memory: Whether to maintain conversation history
            memory_window: Number of messages to keep in memory
        """
        self.llm_provider = llm_provider or Config.LLM_PROVIDER
        self.enable_memory = enable_memory
        self.memory_window = memory_window
        
        # Initialize components
        self.retriever = self._init_retriever()
        self.llm = self._init_llm()
        self.citation_manager = CitationManager()
        
        # Initialize conversation memory
        if self.enable_memory:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                human_prefix="User",
                ai_prefix="Assistant"
            )
        else:
            self.memory = None
        
        # Conversation history for display
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Setup prompt template
        self._setup_prompts()
        
        print(f"✅ RAG Agent initialized with {self.llm_provider} LLM")
    
    def _init_retriever(self) -> Retriever:
        """Initialize retriever with Qdrant connections."""
        try:
            retriever = Retriever(
                qdrant_host=Config.QDRANT_HOST,
                qdrant_port=Config.QDRANT_PORT,
                text_collection=Config.COLLECTION_TEXT,
                image_collection=Config.COLLECTION_IMAGE,
                use_gpu=Config.USE_GPU
            )
            
            # Health check
            health = retriever.health_check()
            print("\n🔍 Retriever Health Check:")
            for component, status in health.items():
                print(f"  • {component}: {status}")
            
            return retriever
            
        except Exception as e:
            print(f"❌ Failed to initialize retriever: {e}")
            raise
    
    def _init_llm(self):
        """Initialize LLM based on provider."""
        try:
            if self.llm_provider == "groq":
                from langchain_groq import ChatGroq
                
                if not Config.GROQ_API_KEY:
                    raise ValueError("GROQ_API_KEY not set")
                
                print(f"🤖 Initializing Groq LLM...")
                llm = ChatGroq(
                    api_key=Config.GROQ_API_KEY,
                    model_name="llama-3.3-70b-versatile",
                    temperature=Config.TEMPERATURE,
                    max_tokens=Config.MAX_TOKENS
                )
                return llm
            
            elif self.llm_provider == "openai":
                from langchain_openai import ChatOpenAI
                
                if not Config.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not set")
                
                print(f"🤖 Initializing OpenAI LLM...")
                llm = ChatOpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    model_name="gpt-3.5-turbo",
                    temperature=Config.TEMPERATURE,
                    max_tokens=Config.MAX_TOKENS
                )
                return llm
            
            elif self.llm_provider == "local":
                from langchain_community.llms import Ollama
                
                print(f"🤖 Initializing Local Ollama LLM...")
                llm = Ollama(
                    base_url=Config.OLLAMA_BASE_URL,
                    model=Config.OLLAMA_MODEL,
                    temperature=Config.TEMPERATURE,
                    num_predict=Config.MAX_TOKENS
                )
                return llm
            
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
        
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            raise
    
    def _setup_prompts(self):
        """Setup LLM prompt templates."""
        self.rag_prompt = PromptTemplate(
            template="""You are a helpful Wikipedia expert assistant answering questions with accurate information.

Use the provided context from Wikipedia articles and images to answer the user's question accurately.
Always cite your sources using the format [1], [2], etc., referring to the bibliography at the end.

If the context doesn't contain information to answer the question, say "I don't have enough information to answer this question."

Context from Wikipedia:
{context}

Conversation history:
{chat_history}

User Question: {question}

Please provide a comprehensive answer with citations.""",
            input_variables=["context", "chat_history", "question"]
        )
    
    def process_query(
        self,
        user_query: str,
        text_k: int = 3,
        image_k: int = 3
    ) -> Dict[str, Any]:
        """
        Process a user query with multimodal retrieval.
        
        Args:
            user_query: User's question
            text_k: Number of text results to retrieve
            image_k: Number of image results to retrieve
            
        Returns:
            Dict with:
            - answer: LLM response
            - citations: List of formatted citations
            - images: List of retrieved images
            - metadata: Processing metadata
        """
        print(f"\n{'='*60}")
        print(f"Processing query: {user_query}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        try:
            # Clear previous citations
            self.citation_manager.clear()
            
            # Retrieve relevant content
            print("\n📚 Retrieving relevant content...")
            retrieval_result = self.retriever.retrieve_multimodal(
                query=user_query,
                text_k=text_k,
                image_k=image_k
            )

            print("\n=== RETRIEVAL DEBUG ===")
            print("Text results count:", len(retrieval_result["texts"]))
            print("Image results count:", len(retrieval_result["images"]))


            for i, t in enumerate(retrieval_result["texts"]):
                print(f"\nText {i+1} title:", t.get("title"))
                print("Score:", t.get("score"))

            for i, img in enumerate(retrieval_result["images"]):
                print(f"\nImage {i+1}:", img.get("image_name"))
            print("=== END DEBUG ===\n")
            
            # Extract and format context
            text_results = retrieval_result["texts"]
            image_results = retrieval_result["images"]
            
            # Add citations
            print("\n📝 Processing citations...")
            for text_result in text_results:
                self.citation_manager.add_text_citation(
                    title=text_result["title"],
                    source_url=text_result["source"],
                    score=text_result["score"],
                    snippet=text_result["text"][:150]
                )
            
            for image_result in image_results:
                self.citation_manager.add_image_citation(
                    image_name=image_result["image_name"],
                    image_path=image_result["minio_path"],
                    score=image_result["score"]
                )
            
            # Build context from retrieved texts
            context_parts = []
            for i, result in enumerate(text_results, 1):
                context_parts.append(
                    f"[{i}] {result['title']} (Score: {result['score']:.2f}):\n{result['text']}"
                )
            
            context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."
            
            # Get chat history for context
            chat_history = self._get_chat_history_string() if self.memory else ""
            
            # Generate response with LLM
            print("\n🧠 Generating response...")
            response = self.llm.invoke([
                {"role": "system", "content": "You are a helpful Wikipedia expert assistant. Always cite sources."},
                {"role": "user", "content": f"""Context from Wikipedia:
{context}

User Question: {user_query}

Please answer the question using the provided context. Cite sources as [1], [2], etc."""}
            ])
            
            answer = response.content
            
            # Add to memory
            if self.memory:
                self.memory.chat_memory.add_user_message(user_query)
                self.memory.chat_memory.add_ai_message(answer)
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "content": user_query
            })
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": answer
            })
            
            # Format citations
            formatted_citations = self.citation_manager.format_citations()
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "answer": answer,
                "citations": formatted_citations,
                "images": image_results,
                "metadata": {
                    "query": user_query,
                    "text_results": len(text_results),
                    "image_results": len(image_results),
                    "total_sources": self.citation_manager.count(),
                    "processing_time_seconds": round(elapsed_time, 2),
                    "llm_provider": self.llm_provider
                }
            }
            
            print(f"\n✅ Response generated in {elapsed_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            return {
                "success": False,
                "answer": f"Error: {str(e)}",
                "citations": [],
                "images": [],
                "metadata": {
                    "error": str(e)
                }
            }
    
    def _get_chat_history_string(self) -> str:
        """Get formatted chat history string."""
        if not self.memory or not self.memory.chat_memory.messages:
            return ""
        
        # Get last N messages for context window
        messages = self.memory.chat_memory.messages[-self.memory_window*2:]
        
        history_parts = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                history_parts.append(f"Assistant: {msg.content}")
        
        return "\n".join(history_parts)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get full conversation history.
        
        Returns:
            List of conversation turns
        """
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        if self.memory:
            self.memory.clear()
        self.citation_manager.clear()
        print("✅ Conversation history cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status information.
        
        Returns:
            Dict with agent status
        """
        return {
            "llm_provider": self.llm_provider,
            "memory_enabled": self.enable_memory,
            "conversation_turns": len(self.conversation_history),
            "total_citations": self.citation_manager.count(),
            "models": {
                "embeddings": Config.EMBEDDING_MODEL,
                "vision": f"{Config.CLIP_MODEL} ({Config.CLIP_PRETRAINED})"
            }
        }
