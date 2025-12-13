"""Check Pinecone index dimensions."""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "rag-educational-content")

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Get index stats
stats = index.describe_index_stats()
print(f"Index: {index_name}")
print(f"Dimensions: {index.describe_index_stats().get('dimension', 'Unknown')}")
print(f"Total vectors: {stats.get('total_vector_count', 0)}")

# Try to get full index description
try:
    # For newer Pinecone API
    index_info = pc.describe_index(index_name)
    print(f"\nFull Index Info:")
    print(f"  Name: {index_info.name}")
    print(f"  Dimension: {index_info.dimension}")
    print(f"  Metric: {index_info.metric}")
    print(f"  Spec: {index_info.spec}")
except Exception as e:
    print(f"\nCould not get full details: {e}")
    print("Note: If dimensions are 1024, you need to delete and recreate with 1536")

