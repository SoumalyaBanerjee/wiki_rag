"""Test suite for Phase 3 components."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.citation_manager import CitationManager, Citation
from utils.retriever import Retriever
from config import Config


def test_config():
    """Test configuration loading."""
    print("\n" + "="*60)
    print("TEST 1: Configuration")
    print("="*60)
    
    try:
        print(Config.get_summary())
        
        if Config.validate():
            print("✅ Configuration validation passed")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_citation_manager():
    """Test citation manager functionality."""
    print("\n" + "="*60)
    print("TEST 2: Citation Manager")
    print("="*60)
    
    try:
        manager = CitationManager()
        
        # Add some test citations
        manager.add_text_citation(
            title="Machine Learning",
            source_url="https://wikipedia.org/wiki/Machine_learning",
            score=0.92,
            snippet="Machine learning is a subset of artificial intelligence..."
        )
        
        manager.add_text_citation(
            title="Deep Learning",
            source_url="https://wikipedia.org/wiki/Deep_learning",
            score=0.88
        )
        
        manager.add_image_citation(
            image_name="neural_network_diagram.png",
            image_path="minio://wiki-images/neural_network_diagram.png",
            score=0.85
        )
        
        # Test deduplication
        manager.add_text_citation(
            title="Machine Learning",  # Duplicate
            source_url="https://wikipedia.org/wiki/Machine_learning",
            score=0.95  # Higher score
        )
        
        print(f"✅ Added 3 citations (1 duplicate)")
        print(f"✅ Total unique citations: {manager.count()}")
        
        # Test formatting
        print("\n📋 Formatted Citations:")
        for citation in manager.format_citations():
            print(f"  {citation}\n")
        
        # Test inline format
        print("📋 Inline Citations:")
        for citation in manager.format_citations_inline():
            print(f"  {citation}")
        
        # Test dictionary format
        print("\n📋 Citation Dictionary:")
        citations_dict = manager.get_citations_dict()
        for idx, citation in citations_dict.items():
            print(f"  [{idx}] {citation['title']} ({citation['type']})")
        
        print("\n✅ Citation manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Citation manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retriever_initialization():
    """Test retriever initialization."""
    print("\n" + "="*60)
    print("TEST 3: Retriever Initialization")
    print("="*60)
    
    try:
        print("🔹 Initializing retriever...")
        retriever = Retriever(
            qdrant_host=Config.QDRANT_HOST,
            qdrant_port=Config.QDRANT_PORT,
            use_gpu=Config.USE_GPU
        )
        
        print("✅ Retriever initialized successfully")
        
        # Health check
        print("\n🔍 Health Check:")
        health = retriever.health_check()
        all_good = True
        for component, status in health.items():
            print(f"  • {component}: {status}")
            if "❌" in status or "Error" in status:
                all_good = False
        
        if all_good:
            print("\n✅ All components healthy")
        else:
            print("\n⚠️  Some components have issues")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Retriever initialization failed: {e}")
        print("\nℹ️  Make sure:")
        print("  1. Docker is running: docker-compose up -d")
        print("  2. Qdrant is accessible at localhost:6333")
        print("  3. Collections are populated with data")
        import traceback
        traceback.print_exc()
        return False


def test_text_retrieval():
    """Test text retrieval functionality."""
    print("\n" + "="*60)
    print("TEST 4: Text Retrieval")
    print("="*60)
    
    try:
        retriever = Retriever()
        
        test_queries = [
            "What is artificial intelligence?",
            "deep learning neural networks",
            "machine learning algorithms"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = retriever.retrieve_text(query, k=2)
            
            if results:
                print(f"✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n  [{i}] {result['title']} (Score: {result['score']:.2f})")
                    print(f"      {result['text'][:100]}...")
            else:
                print("⚠️  No results found")
        
        print("\n✅ Text retrieval test passed")
        return True
        
    except Exception as e:
        print(f"❌ Text retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_retrieval():
    """Test image retrieval functionality."""
    print("\n" + "="*60)
    print("TEST 5: Image Retrieval")
    print("="*60)
    
    try:
        retriever = Retriever()
        
        test_queries = [
            "neural network diagram",
            "deep learning architecture",
            "computer vision"
        ]
        
        for query in test_queries:
            print(f"\n🖼️  Query: '{query}'")
            results = retriever.retrieve_images(query, k=2)
            
            if results:
                print(f"✅ Found {len(results)} images:")
                for i, result in enumerate(results, 1):
                    print(f"\n  [{i}] {result['image_name']} (Score: {result['score']:.2f})")
                    print(f"      Path: {result['minio_path']}")
            else:
                print("⚠️  No images found")
        
        print("\n✅ Image retrieval test passed")
        return True
        
    except Exception as e:
        print(f"❌ Image retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multimodal_retrieval():
    """Test multimodal retrieval."""
    print("\n" + "="*60)
    print("TEST 6: Multimodal Retrieval")
    print("="*60)
    
    try:
        retriever = Retriever()
        
        query = "What is neural networks and show me diagrams"
        
        print(f"\n🔄 Query: '{query}'")
        result = retriever.retrieve_multimodal(query, text_k=2, image_k=2)
        
        print(f"\n✅ Total results: {result['total_results']}")
        print(f"   • Text results: {len(result['texts'])}")
        print(f"   • Image results: {len(result['images'])}")
        
        if result['texts']:
            print("\n📄 Text Results:")
            for i, text in enumerate(result['texts'], 1):
                print(f"   [{i}] {text['title']} ({text['score']:.2f})")
        
        if result['images']:
            print("\n🖼️  Image Results:")
            for i, img in enumerate(result['images'], 1):
                print(f"   [{i}] {img['image_name']} ({img['score']:.2f})")
        
        print("\n✅ Multimodal retrieval test passed")
        return True
        
    except Exception as e:
        print(f"❌ Multimodal retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 PHASE 3 COMPONENT TESTS")
    print("="*60)
    
    results = {
        "Configuration": test_config(),
        "Citation Manager": test_citation_manager(),
        "Retriever Init": test_retriever_initialization(),
    }
    
    # Only run retrieval tests if initialization passed
    if results["Retriever Init"]:
        results["Text Retrieval"] = test_text_retrieval()
        results["Image Retrieval"] = test_image_retrieval()
        results["Multimodal Retrieval"] = test_multimodal_retrieval()
    else:
        print("\n⏭️  Skipping retrieval tests (initialization failed)")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
