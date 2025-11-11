"""
Test script for Gemini File Search integration
Run this to verify the refactoring is working correctly
"""

import os
import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, create_engine
from app.config import settings
from app.model.document_model import Document, GeminiFileSearchStore
from app.service.gemini_file_search_service import GeminiFileSearchService
from app.utils import set_snowflake_generator
from snowflake import SnowflakeGenerator


def test_file_search_service():
    """Test Gemini File Search Service functionality"""
    print("=" * 60)
    print("Testing Gemini File Search Integration")
    print("=" * 60)

    # Initialize Snowflake ID generator
    import os
    worker_id = os.getpid() % 1024
    snowflake_gen = SnowflakeGenerator(worker_id)
    set_snowflake_generator(snowflake_gen)
    print("✅ Snowflake ID generator initialized")

    # Check API key
    if not settings.GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not configured!")
        print("   Please set GEMINI_API_KEY in your .env file")
        return False

    print("✅ Gemini API key found")

    # Initialize service
    try:
        gemini_service = GeminiFileSearchService()
        print("✅ GeminiFileSearchService initialized")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return False

    # Test database connection
    try:
        DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        engine = create_engine(DATABASE_URL)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    # Test creating a File Search Store
    print("\nTesting File Search Store creation...")
    try:
        with Session(engine) as session:
            test_user_id = 999999  # Test user ID

            # Create store
            store = gemini_service.create_file_search_store(
                db=session,
                user_id=test_user_id,
                display_name="Test Store",
                description="Test store for validation"
            )

            print(f"✅ Created File Search Store:")
            print(f"   - ID: {store.id}")
            print(f"   - Store Name: {store.store_name}")
            print(f"   - Display Name: {store.display_name}")

            # Create a test text file
            test_content = """
            This is a test document for Gemini File Search.
            It contains information about machine learning and artificial intelligence.
            Machine learning is a subset of AI that focuses on learning from data.
            """

            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
                tmp_file.write(test_content)
                tmp_file_path = tmp_file.name

            print("\n✅ Created test document")

            # Upload document to store
            print("\nTesting document upload...")
            try:
                document = gemini_service.upload_file_to_store(
                    db=session,
                    file_path=tmp_file_path,
                    store_id=store.id,
                    filename="test_document.txt",
                    user_id=test_user_id,
                    metadata={"test": "true", "purpose": "validation"}
                )

                print(f"✅ Uploaded document:")
                print(f"   - ID: {document.id}")
                print(f"   - Filename: {document.filename}")
                print(f"   - Gemini File ID: {document.gemini_file_id}")
                print(f"   - Status: {document.status}")

            except Exception as e:
                print(f"❌ Document upload failed: {e}")
                # Clean up
                os.unlink(tmp_file_path)
                gemini_service.delete_store(session, store.id, force=True)
                return False

            # Clean up temp file
            os.unlink(tmp_file_path)

            # Test RAG query
            print("\nTesting RAG query...")
            try:
                result = gemini_service.query_with_file_search(
                    query="What is machine learning?",
                    store_name=store.store_name,
                    model=settings.GEMINI_FILE_SEARCH_MODEL
                )

                print(f"✅ RAG query successful:")
                print(f"   - Model: {result['model']}")
                print(f"   - Response length: {len(result['content'])} characters")
                print(f"   - Has grounding metadata: {'grounding_metadata' in result}")
                print(f"\n   Response preview:")
                print(f"   {result['content'][:200]}...")

            except Exception as e:
                print(f"❌ RAG query failed: {e}")
                # Clean up
                gemini_service.delete_document(session, document.id, delete_from_gemini=True)
                gemini_service.delete_store(session, store.id, force=True)
                return False

            # Test document listing
            print("\nTesting document listing...")
            try:
                documents = gemini_service.list_documents(
                    db=session,
                    user_id=test_user_id
                )

                print(f"✅ Document listing successful:")
                print(f"   - Found {len(documents)} document(s)")

            except Exception as e:
                print(f"❌ Document listing failed: {e}")

            # Clean up test data
            print("\nCleaning up test data...")
            try:
                # Delete document
                gemini_service.delete_document(
                    db=session,
                    document_id=document.id,
                    delete_from_gemini=True
                )
                print("✅ Deleted test document")

                # Delete store
                gemini_service.delete_store(
                    db=session,
                    store_id=store.id,
                    force=True
                )
                print("✅ Deleted test store")

            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_file_search_service()
    sys.exit(0 if success else 1)
