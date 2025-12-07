"""
Test script to investigate document retrieval issue
"""
import hashlib
from sqlmodel import Session, select
import sys
import os

# Add backend to path
sys.path.insert(0, '/app/backend')

from app.model.document_model import Document, GeminiFileSearchStore
import app.model

# Test Gemini API key (replace with your actual key)
TEST_API_KEY = os.getenv('GEMINI_API_KEY', '')

if not TEST_API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set")
    sys.exit(1)

# Calculate hash
api_key_hash = hashlib.sha256(TEST_API_KEY.encode()).hexdigest()
print(f"API Key Hash: {api_key_hash}")
print(f"API Key Hash (first 8 chars): {api_key_hash[:8]}")
print()

# Connect to database
with Session(app.model.engine) as session:
    # Get all stores
    print("=== ALL STORES ===")
    all_stores = session.exec(select(GeminiFileSearchStore)).all()
    for store in all_stores:
        print(f"Store ID: {store.id}")
        print(f"  User ID: {store.user_id}")
        print(f"  Store Name: {store.store_name}")
        print(f"  Display Name: {store.display_name}")
        print(f"  API Key Hash: {store.api_key_hash}")
        print(f"  API Key Hash (first 8): {store.api_key_hash[:8] if store.api_key_hash else 'N/A'}")
        print(f"  Is Active: {store.is_active}")
        print(f"  Document Count: {store.document_count}")
        print(f"  Total Size: {store.total_size_bytes}")
        print()

    # Get all documents
    print("=== ALL DOCUMENTS ===")
    all_docs = session.exec(select(Document)).all()
    for doc in all_docs:
        print(f"Doc ID: {doc.id}")
        print(f"  User ID: {doc.user_id}")
        print(f"  Filename: {doc.filename}")
        print(f"  Store ID: {doc.gemini_store_id}")
        print(f"  Status: {doc.status}")
        print()

    # Find stores matching the test API key
    print("=== STORES MATCHING TEST API KEY ===")
    matching_stores = session.exec(
        select(GeminiFileSearchStore).where(
            GeminiFileSearchStore.api_key_hash == api_key_hash
        )
    ).all()
    print(f"Found {len(matching_stores)} stores with matching API key hash")
    for store in matching_stores:
        print(f"Store ID: {store.id}, Active: {store.is_active}, User: {store.user_id}")

        # Find documents in this store
        docs_in_store = session.exec(
            select(Document).where(
                Document.gemini_store_id == store.store_name
            )
        ).all()
        print(f"  Documents in this store: {len(docs_in_store)}")
        for doc in docs_in_store:
            print(f"    - {doc.filename} (User: {doc.user_id})")
    print()
