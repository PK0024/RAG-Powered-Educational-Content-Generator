"""Quick test script to verify Pinecone connection."""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load .env file
load_dotenv()

# Get credentials
api_key = os.getenv("PINECONE_API_KEY")
environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
index_name = os.getenv("PINECONE_INDEX_NAME", "rag-educational-content")

print("Testing Pinecone connection...")
print(f"API Key: {api_key[:10]}..." if api_key else "[ERROR] API Key not found!")
print(f"Environment: {environment}")
print(f"Index Name: {index_name}")
print()

if not api_key:
    print("[ERROR] PINECONE_API_KEY not found in .env file!")
    exit(1)

try:
    # Initialize Pinecone
    print("1. Initializing Pinecone client...")
    pc = Pinecone(api_key=api_key)
    print("   [OK] Pinecone client initialized")
    
    # List indexes
    print("2. Listing existing indexes...")
    indexes = pc.list_indexes()
    index_names = [idx.name for idx in indexes]
    print(f"   Found {len(index_names)} indexes: {index_names}")
    
    # Check if our index exists
    if index_name in index_names:
        print(f"   [OK] Index '{index_name}' exists")
    else:
        print(f"   [INFO] Index '{index_name}' does not exist (will be created on first use)")
    
    print()
    print("[SUCCESS] Pinecone connection test PASSED!")
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {str(e)}")
    print()
    print("Common issues:")
    print("1. Invalid API key - check your .env file")
    print("2. API key doesn't have permission to list/create indexes")
    print("3. Wrong environment/region")
    exit(1)

