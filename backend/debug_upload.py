"""Debug script to test PDF upload process step by step."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

load_dotenv()

print("=== Debugging PDF Upload Process ===\n")

# 1. Check environment variables
print("1. Checking environment variables...")
openai_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

if not openai_key or openai_key == "your_openai_api_key_here":
    print("   [ERROR] OPENAI_API_KEY not set or still has placeholder value!")
else:
    print(f"   [OK] OPENAI_API_KEY: {openai_key[:10]}...")

if not pinecone_key or pinecone_key == "your_pinecone_api_key_here":
    print("   [ERROR] PINECONE_API_KEY not set or still has placeholder value!")
else:
    print(f"   [OK] PINECONE_API_KEY: {pinecone_key[:10]}...")

if not pinecone_env:
    print("   [ERROR] PINECONE_ENVIRONMENT not set!")
else:
    print(f"   [OK] PINECONE_ENVIRONMENT: {pinecone_env}")

print()

# 2. Test imports
print("2. Testing imports...")
try:
    from rag_edu_generator.config import settings
    print("   [OK] Config loaded")
except Exception as e:
    print(f"   [ERROR] Config failed: {e}")
    exit(1)

try:
    from rag_edu_generator.services.pdf_extractor import PDFExtractor
    print("   [OK] PDFExtractor imported")
except Exception as e:
    print(f"   [ERROR] PDFExtractor import failed: {e}")
    exit(1)

try:
    from rag_edu_generator.services.vector_store import VectorStoreService
    print("   [OK] VectorStoreService imported")
except Exception as e:
    print(f"   [ERROR] VectorStoreService import failed: {e}")
    exit(1)

try:
    from rag_edu_generator.services.rag_service import RAGService
    print("   [OK] RAGService imported")
except Exception as e:
    print(f"   [ERROR] RAGService import failed: {e}")
    exit(1)

print()

# 3. Test service initialization
print("3. Testing service initialization...")
try:
    vector_store = VectorStoreService()
    print("   [OK] VectorStoreService initialized")
except Exception as e:
    print(f"   [ERROR] VectorStoreService initialization failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    rag_service = RAGService(vector_store)
    print("   [OK] RAGService initialized")
except Exception as e:
    print(f"   [ERROR] RAGService initialization failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()
print("[SUCCESS] All basic checks passed!")
print("\nIf upload still fails, check the backend terminal for the actual error message.")

