"""
Document Synchronization Service
Ensures consistency between Gemini File Search and local database
"""

import logging
from typing import Optional, Tuple
from google import genai
from sqlmodel import Session, select
from pathlib import Path

from app.model.document_model import Document, GeminiFileSearchStore
from app.utils import get_timestamp

logger = logging.getLogger(__name__)


class DocumentSyncService:
    """Service to maintain consistency between Gemini and database"""

    def __init__(self, gemini_client: genai.Client, api_key_hash: str):
        """
        Initialize sync service

        Args:
            gemini_client: Initialized Gemini API client
            api_key_hash: Hash of the API key being used
        """
        self.client = gemini_client
        self.api_key_hash = api_key_hash

    def sync_store_documents(
        self, db: Session, store: GeminiFileSearchStore
    ) -> Tuple[int, int]:
        """
        Synchronize a store's documents from Gemini to database

        This method:
        1. Fetches all documents from Gemini for the store
        2. Compares with database records
        3. Adds missing documents to database
        4. Updates store document count

        Args:
            db: Database session
            store: Store to synchronize

        Returns:
            Tuple of (documents_added, documents_removed)
        """
        logger.info(f"Syncing store {store.display_name} ({store.store_name})")

        try:
            # Get all documents from Gemini
            gemini_docs = list(
                self.client.file_search_stores.documents.list(parent=store.store_name)
            )
            gemini_doc_ids = {doc.name for doc in gemini_docs}

            logger.info(
                f"Found {len(gemini_docs)} documents in Gemini for store {store.store_name}"
            )

            # Get all documents from database for this store
            db_docs_stmt = select(Document).where(
                Document.gemini_store_id == store.store_name
            )
            db_docs = list(db.exec(db_docs_stmt).all())
            db_doc_map = {doc.gemini_file_id: doc for doc in db_docs}

            logger.info(
                f"Found {len(db_docs)} documents in database for store {store.store_name}"
            )

            documents_added = 0
            documents_removed = 0

            # Add documents that exist in Gemini but not in database
            for gemini_doc in gemini_docs:
                if gemini_doc.name not in db_doc_map:
                    logger.warning(
                        f"Document {gemini_doc.name} exists in Gemini but not in database, adding..."
                    )

                    # Extract metadata
                    display_name = (
                        gemini_doc.display_name
                        if hasattr(gemini_doc, "display_name")
                        else "Unknown"
                    )
                    file_type = (
                        Path(display_name).suffix.lstrip(".").lower() or "unknown"
                    )

                    # Create database record
                    new_doc = Document(
                        user_id=store.user_id,
                        filename=display_name,
                        file_type=file_type,
                        file_size=0,  # Unknown - could fetch from Gemini if needed
                        content_hash="synced_from_gemini",  # Placeholder
                        source_url=None,
                        gemini_file_id=gemini_doc.name,
                        gemini_store_id=store.store_name,
                        gemini_mime_type="text/plain",  # Default
                        gemini_metadata=None,
                        status="completed",
                        error_message=None,
                    )

                    db.add(new_doc)
                    documents_added += 1

            # Remove documents that exist in database but not in Gemini
            # (This means they were deleted from Gemini outside of our app)
            for db_doc in db_docs:
                if db_doc.gemini_file_id not in gemini_doc_ids:
                    logger.warning(
                        f"Document {db_doc.gemini_file_id} exists in database but not in Gemini, removing from database..."
                    )
                    db.delete(db_doc)
                    documents_removed += 1

            # Update store statistics
            store.document_count = len(gemini_docs)
            store.updated_at = get_timestamp()

            db.commit()

            logger.info(
                f"Sync complete: {documents_added} added, {documents_removed} removed"
            )

            return (documents_added, documents_removed)

        except Exception as e:
            logger.error(f"Error syncing store {store.store_name}: {e}")
            db.rollback()
            raise

    def verify_document_consistency(
        self, db: Session, store: GeminiFileSearchStore
    ) -> bool:
        """
        Verify that database and Gemini are in sync for a store

        Args:
            db: Database session
            store: Store to verify

        Returns:
            True if consistent, False otherwise
        """
        try:
            # Get document counts
            gemini_docs = list(
                self.client.file_search_stores.documents.list(parent=store.store_name)
            )
            gemini_count = len(gemini_docs)

            db_docs_stmt = select(Document).where(
                Document.gemini_store_id == store.store_name
            )
            db_count = len(list(db.exec(db_docs_stmt).all()))

            if gemini_count != db_count:
                logger.warning(
                    f"Inconsistency detected in store {store.store_name}: "
                    f"Gemini has {gemini_count} documents, database has {db_count}"
                )
                return False

            logger.info(f"Store {store.store_name} is consistent ({gemini_count} documents)")
            return True

        except Exception as e:
            logger.error(f"Error verifying consistency for store {store.store_name}: {e}")
            return False
