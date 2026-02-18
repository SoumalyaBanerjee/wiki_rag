"""Unified retriever for text and image search."""

from typing import List, Dict, Optional
import torch
import open_clip
from PIL import Image
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from minio import Minio


class Retriever:
    """
    Unified retriever for multimodal search.
    
    Supports:
    - Text-to-text search (Wikipedia articles)
    - Text-to-image search (CLIP embeddings)
    - Image-to-image search (future)
    
    Uses:
    - Qdrant for vector storage
    - sentence-transformers for text embeddings
    - OpenCLIP for image/multimodal embeddings
    """
    
    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        text_collection: str = "wiki_text_poc",
        image_collection: str = "wiki_image_poc",
        use_gpu: bool = False
    ):
        """
        Initialize retriever.
        
        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            text_collection: Qdrant collection name for text
            image_collection: Qdrant collection name for images
            use_gpu: Whether to use GPU for embeddings
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"🔹 Using device: {self.device}")
        
        # Initialize Qdrant client
        try:
            self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
            print(f"✅ Connected to Qdrant at {qdrant_host}:{qdrant_port}")
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant: {e}")
            raise
        
        self.text_collection = text_collection
        self.image_collection = image_collection
        
        # Initialize text embedding model
        try:
            print("🔹 Loading sentence-transformers model...")
            self.text_embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✅ Text embedding model loaded")
        except Exception as e:
            print(f"❌ Failed to load text embeddings: {e}")
            raise
        
        # Initialize OpenCLIP model for images
        try:
            print("🔹 Loading OpenCLIP model...")
            self.clip_model, self.clip_preprocess, self.clip_tokenizer = (
                open_clip.create_model_and_transforms(
                    model_name="ViT-B-32",
                    pretrained="laion2b_s34b_b79k"
                )
            )
            self.clip_model = self.clip_model.to(self.device)
            self.clip_model.eval()
            print("✅ OpenCLIP model loaded (ViT-B-32)")
        except Exception as e:
            print(f"❌ Failed to load OpenCLIP model: {e}")
            raise
    
    def retrieve_text(
        self,
        query: str,
        k: int = 3,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for relevant text documents.
        
        Args:
            query: Search query string
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of dicts with:
            - text: chunk content
            - score: similarity score
            - title: document title
            - source: document URL
            - metadata: full metadata dict
        """
        try:
            print(f"🔍 Text search: '{query}' (top-{k})")
            
            # Embed the query
            query_vector = self.text_embeddings.embed_query(query)
            
            # Search Qdrant
            results = self.qdrant.search(
                collection_name=self.text_collection,
                query_vector=query_vector,
                limit=k
            )
            
            # Format results
            formatted_results = []
            for hit in results:
                if hit.score < score_threshold:
                    continue
                
                formatted_results.append({
                    "text": hit.payload.get("text", ""),
                    "score": float(hit.score),
                    "title": hit.payload.get("title", "Unknown"),
                    "source": hit.payload.get("source", ""),
                    "metadata": hit.payload
                })
            
            print(f"✅ Found {len(formatted_results)} text results")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Text search failed: {e}")
            return []
    
    def retrieve_images(
        self,
        query: str,
        k: int = 3,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for relevant images using text query.
        
        Args:
            query: Text description of images to find
            k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of dicts with:
            - image_name: filename
            - score: similarity score
            - bucket: MinIO bucket name
            - minio_path: full path to image
            - metadata: full metadata dict
        """
        try:
            print(f"🖼️  Image search: '{query}' (top-{k})")
            
            # Encode text query with OpenCLIP
            with torch.no_grad():
                text_tokens = open_clip.tokenize([query]).to(self.device)
                query_vector = self.clip_model.encode_text(text_tokens)
                query_vector /= query_vector.norm(dim=-1, keepdim=True)
            
            # Search Qdrant
            results = self.qdrant.search(
                collection_name=self.image_collection,
                query_vector=query_vector.squeeze().tolist(),
                limit=k
            )
            
            # Format results
            formatted_results = []
            for hit in results:
                if hit.score < score_threshold:
                    continue
                
                formatted_results.append({
                    "image_name": hit.payload.get("image_name", ""),
                    "score": float(hit.score),
                    "bucket": hit.payload.get("bucket", "wiki-images"),
                    "minio_path": f"minio://{hit.payload.get('bucket', 'wiki-images')}/{hit.payload.get('image_name', '')}",
                    "metadata": hit.payload
                })
            
            print(f"✅ Found {len(formatted_results)} image results")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Image search failed: {e}")
            return []
    
    def retrieve_multimodal(
        self,
        query: str,
        text_k: int = 3,
        image_k: int = 3,
        text_threshold: float = 0.0,
        image_threshold: float = 0.0
    ) -> Dict:
        """
        Perform unified multimodal search.
        
        Args:
            query: Search query
            text_k: Number of text results
            image_k: Number of image results
            text_threshold: Minimum text similarity
            image_threshold: Minimum image similarity
            
        Returns:
            Dict with:
            - query: original query
            - texts: list of text results
            - images: list of image results
            - total_results: count of results
        """
        print(f"\n🔄 Multimodal search: '{query}'")
        
        texts = self.retrieve_text(query, k=text_k, score_threshold=text_threshold)
        images = self.retrieve_images(query, k=image_k, score_threshold=image_threshold)
        
        return {
            "query": query,
            "texts": texts,
            "images": images,
            "total_results": len(texts) + len(images)
        }
    
    def health_check(self) -> Dict:
        """
        Check if retriever is properly initialized.
        
        Returns:
            Dict with health status
        """
        status = {
            "qdrant": "❌ Offline",
            "text_collection": "❌ Missing",
            "image_collection": "❌ Missing",
            "embeddings": "✅ Ready",
            "clip_model": "✅ Ready"
        }
        
        try:
            collections = self.qdrant.get_collections().collections
            collection_names = [c.name for c in collections]
            
            status["qdrant"] = "✅ Online"
            status["text_collection"] = (
                "✅ Ready" 
                if self.text_collection in collection_names 
                else "❌ Missing"
            )
            status["image_collection"] = (
                "✅ Ready" 
                if self.image_collection in collection_names 
                else "❌ Missing"
            )
            
        except Exception as e:
            status["qdrant"] = f"❌ Error: {str(e)[:50]}"
        
        return status
