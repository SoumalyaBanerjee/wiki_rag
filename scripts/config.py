"""Configuration management for Phase 3 agent."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings for RAG agent."""
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Qdrant Configuration
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    
    # Collection Names
    COLLECTION_TEXT = os.getenv("COLLECTION_TEXT", "wiki_text_poc")
    COLLECTION_IMAGE = os.getenv("COLLECTION_IMAGE", "wiki_image_poc")
    
    # Model Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    CLIP_MODEL = "ViT-B-32"
    CLIP_PRETRAINED = "laion2b_s34b_b79k"
    
    # Agent Parameters
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "3"))
    
    # Feature Flags
    USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
    ENABLE_IMAGE_SEARCH = True
    ENABLE_TEXT_SEARCH = True
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if valid, False otherwise
        """
        errors = []
        
        # Check LLM provider
        valid_providers = ["groq", "openai", "local"]
        if cls.LLM_PROVIDER not in valid_providers:
            errors.append(f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be one of {valid_providers}")
        
        # Check API keys for specific providers
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY not set but LLM_PROVIDER=groq")
        
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set but LLM_PROVIDER=openai")
        
        # Check Qdrant connectivity
        if not cls.QDRANT_HOST:
            errors.append("QDRANT_HOST not set")
        
        if errors:
            print("⚠️  Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_summary(cls) -> str:
        """
        Return configuration summary.
        
        Returns:
            Formatted configuration string
        """
        summary = f"""
╔══════════════════════════════════════╗
║   RAG Agent Configuration             ║
╚══════════════════════════════════════╝

LLM Configuration:
  • Provider: {cls.LLM_PROVIDER}
  • Max Tokens: {cls.MAX_TOKENS}
  • Temperature: {cls.TEMPERATURE}

Qdrant Configuration:
  • Host: {cls.QDRANT_HOST}:{cls.QDRANT_PORT}
  • Text Collection: {cls.COLLECTION_TEXT}
  • Image Collection: {cls.COLLECTION_IMAGE}

Models:
  • Embeddings: {cls.EMBEDDING_MODEL}
  • Vision-Language: {cls.CLIP_MODEL} ({cls.CLIP_PRETRAINED})

Retrieval:
  • Top-K Results: {cls.TOP_K_RETRIEVAL}
  • Image Search: {"Enabled" if cls.ENABLE_IMAGE_SEARCH else "Disabled"}
  • Text Search: {"Enabled" if cls.ENABLE_TEXT_SEARCH else "Disabled"}
  • GPU: {"Enabled" if cls.USE_GPU else "Disabled"}
        """
        return summary


# Validate configuration on import
if __name__ == "__main__":
    print(Config.get_summary())
    if Config.validate():
        print("\n✅ Configuration is valid")
    else:
        print("\n❌ Configuration has errors")
