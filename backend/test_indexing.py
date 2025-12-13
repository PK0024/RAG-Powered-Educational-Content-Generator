"""Test script to verify indexing and querying."""

import sys
from pathlib import Path

# Add src to path
backend_path = Path(__file__).parent
src_path = backend_path / "src"
sys.path.insert(0, str(src_path))

from rag_edu_generator.config import settings
from rag_edu_generator.services.vector_store import VectorStoreService
from rag_edu_generator.services.rag_service import RAGService
from pinecone import Pinecone

def check_pinecone_stats():
    """Check current Pinecone index stats."""
    print("\n=== Checking Pinecone Index Stats ===")
    try:
        pc = Pinecone(api_key=settings.pinecone_api_key)
        index = pc.Index(settings.pinecone_index_name)
        stats = index.describe_index_stats()
        
        print(f"Index Name: {settings.pinecone_index_name}")
        print(f"Total Vectors: {stats.get('total_vector_count', 0)}")
        
        namespaces = stats.get('namespaces', {})
        if namespaces:
            print(f"\nNamespaces:")
            for ns, ns_stats in namespaces.items():
                count = ns_stats.get('vector_count', 0)
                print(f"  - {ns}: {count} vectors")
        else:
            print("No namespaces found (using default namespace)")
            
        return stats
    except Exception as e:
        print(f"Error checking Pinecone: {e}")
        return None

def test_query():
    """Test querying the index."""
    print("\n=== Testing Query ===")
    try:
        vector_store_service = VectorStoreService()
        rag_service = RAGService(vector_store_service)
        
        # Try to create query engine
        query_engine = rag_service.create_query_engine(similarity_top_k=3)
        
        # Test query
        result = rag_service.query("what is selenium?", similarity_top_k=3)
        
        print(f"Query: 'what is selenium?'")
        print(f"Answer: {result.get('answer', 'No answer')}")
        print(f"Sources: {len(result.get('sources', []))} sources found")
        
        for i, source in enumerate(result.get('sources', [])[:3]):
            print(f"\nSource {i+1}:")
            print(f"  Text: {source.get('text', '')[:100]}...")
            print(f"  Score: {source.get('score', 'N/A')}")
            print(f"  Metadata: {source.get('metadata', {})}")
            
    except Exception as e:
        print(f"Error during query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Pinecone Indexing Diagnostic ===")
    
    # Check current stats
    stats = check_pinecone_stats()
    
    # Test query
    test_query()
    
    # Check stats again
    print("\n=== Final Stats ===")
    check_pinecone_stats()

