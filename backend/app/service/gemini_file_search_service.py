"""
Gemini File Search Service
Handles all interactions with Google's Gemini File Search API
Replaces the old RAG pipeline with Gemini's built-in RAG capabilities
"""

import os
import hashlib
import mimetypes
import time
from typing import Optional
from pathlib import Path

from google import genai
from google.genai import types
from sqlmodel import Session, select

from app.config import settings
from app.model.document_model import Document, GeminiFileSearchStore
from app.utils import get_timestamp


class GeminiFileSearchService:
    """Service for managing Gemini File Search Stores and documents"""

    def __init__(self, require_api_key: bool = True):
        """
        Initialize Gemini API client

        Args:
            require_api_key: If True, raises error if API key not configured.
                           If False, allows initialization without API key (for DB-only operations)
        """
        self.client = None

        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        elif require_api_key:
            raise ValueError("GEMINI_API_KEY not configured")

    def _ensure_client(self):
        """Ensure Gemini client is initialized before API calls"""
        if not self.client:
            raise ValueError("GEMINI_API_KEY not configured. Cannot perform Gemini API operations.")

    # ===========================
    # File Search Store Management
    # ===========================

    def create_file_search_store(
        self,
        db: Session,
        user_id: Optional[int],
        display_name: str,
        description: Optional[str] = None
    ) -> GeminiFileSearchStore:
        """
        Create a new Gemini File Search Store

        Args:
            db: Database session
            user_id: Owner user ID (None for global store)
            display_name: Human-readable name for the store
            description: Optional description

        Returns:
            GeminiFileSearchStore database record
        """
        self._ensure_client()

        # Create store in Gemini API
        file_search_store = self.client.file_search_stores.create(
            config={'display_name': display_name}
        )

        # Save to database
        db_store = GeminiFileSearchStore(
            user_id=user_id,
            store_name=file_search_store.name,
            display_name=display_name,
            description=description,
            document_count=0,
            total_size_bytes=0,
            is_active=True,
        )
        db.add(db_store)
        db.commit()
        db.refresh(db_store)

        return db_store

    def get_or_create_user_store(
        self,
        db: Session,
        user_id: int
    ) -> GeminiFileSearchStore:
        """
        Get existing store for user or create new one

        Args:
            db: Database session
            user_id: User ID

        Returns:
            GeminiFileSearchStore for the user
        """
        # Check if user already has a store
        statement = select(GeminiFileSearchStore).where(
            GeminiFileSearchStore.user_id == user_id,
            GeminiFileSearchStore.is_active == True
        )
        store = db.exec(statement).first()

        if store:
            return store

        # Create new store for user
        return self.create_file_search_store(
            db=db,
            user_id=user_id,
            display_name=f"User {user_id} Document Store",
            description=f"Personal document store for user {user_id}"
        )

    def get_or_create_global_store(
        self,
        db: Session
    ) -> GeminiFileSearchStore:
        """
        Get existing global store (for non-authenticated users) or create new one

        Args:
            db: Database session

        Returns:
            GeminiFileSearchStore global store (user_id = None)
        """
        # Check if global store already exists
        statement = select(GeminiFileSearchStore).where(
            GeminiFileSearchStore.user_id == None,
            GeminiFileSearchStore.is_active == True
        )
        store = db.exec(statement).first()

        if store:
            return store

        # Create new global store
        return self.create_file_search_store(
            db=db,
            user_id=None,
            display_name="Global Document Store",
            description="Shared document store for all users"
        )

    def list_stores(self, db: Session, user_id: Optional[int] = None) -> list[GeminiFileSearchStore]:
        """
        List all File Search Stores

        Args:
            db: Database session
            user_id: Filter by user ID (None for all stores)

        Returns:
            List of GeminiFileSearchStore records
        """
        statement = select(GeminiFileSearchStore).where(
            GeminiFileSearchStore.is_active == True
        )

        if user_id is not None:
            statement = statement.where(GeminiFileSearchStore.user_id == user_id)

        return list(db.exec(statement).all())

    def delete_store(self, db: Session, store_id: int, force: bool = False) -> bool:
        """
        Delete a File Search Store

        Args:
            db: Database session
            store_id: Store database ID
            force: If True, delete from Gemini API too

        Returns:
            True if successful
        """
        store = db.get(GeminiFileSearchStore, store_id)
        if not store:
            return False

        # Delete from Gemini API if force=True
        if force:
            try:
                self._ensure_client()
                self.client.file_search_stores.delete(
                    name=store.store_name,
                    config={'force': True}
                )
            except Exception as e:
                print(f"Error deleting Gemini store: {e}")

        # Mark as inactive in database
        store.is_active = False
        store.updated_at = get_timestamp()
        db.commit()

        return True

    # ===========================
    # Document Upload & Management
    # ===========================

    def upload_file_to_store(
        self,
        db: Session,
        file_path: str,
        store_id: int,
        filename: str,
        user_id: Optional[int] = None,
        metadata: Optional[dict] = None,
        source_url: Optional[str] = None
    ) -> Document:
        """
        Upload a file to Gemini File Search Store

        Args:
            db: Database session
            file_path: Path to file on disk
            store_id: Database ID of the File Search Store
            filename: Original filename
            user_id: Owner user ID
            metadata: Custom metadata for Gemini (as list of dicts with key/string_value/numeric_value)
            source_url: Original URL if downloaded

        Returns:
            Document database record
        """
        self._ensure_client()

        # Get store from database
        store = db.get(GeminiFileSearchStore, store_id)
        if not store or not store.is_active:
            raise ValueError(f"Store {store_id} not found or inactive")

        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Calculate content hash
        content_hash = self._calculate_file_hash(file_path)

        # Check for duplicates
        statement = select(Document).where(
            Document.content_hash == content_hash,
            Document.gemini_store_id == store.store_name,
            Document.user_id == user_id
        )
        existing_doc = db.exec(statement).first()
        if existing_doc:
            return existing_doc

        # Prepare config for upload
        upload_config = {
            'display_name': filename
        }

        # Add custom metadata if provided
        if metadata:
            # Convert dict to list of metadata entries
            custom_metadata = []
            for key, value in metadata.items():
                if isinstance(value, (int, float)):
                    custom_metadata.append({"key": key, "numeric_value": value})
                else:
                    custom_metadata.append({"key": key, "string_value": str(value)})
            upload_config['custom_metadata'] = custom_metadata

        # Upload to Gemini File Search Store
        try:
            # Upload and import in one step
            operation = self.client.file_search_stores.upload_to_file_search_store(
                file_search_store_name=store.store_name,
                file=file_path,
                config=upload_config
            )

            # Wait for import to complete
            max_wait_time = 300  # 5 minutes
            wait_interval = 2  # 2 seconds
            elapsed_time = 0

            while not operation.done and elapsed_time < max_wait_time:
                time.sleep(wait_interval)
                elapsed_time += wait_interval
                operation = self.client.operations.get(operation)

            if not operation.done:
                raise RuntimeError("File upload timed out after 5 minutes")

            # Check for errors
            if hasattr(operation, 'error') and operation.error:
                raise RuntimeError(f"Upload failed: {operation.error}")

            # Get the document name from the operation response
            if not hasattr(operation, 'response') or not hasattr(operation.response, 'document_name'):
                raise RuntimeError("Failed to get file ID from upload operation")

            gemini_file_id = operation.response.document_name

        except Exception as e:
            raise RuntimeError(f"Failed to upload to Gemini: {str(e)}")

        # Determine file type from extension
        file_type = Path(filename).suffix.lstrip('.').lower() or 'unknown'

        # Create database record
        document = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            content_hash=content_hash,
            source_url=source_url,
            gemini_file_id=gemini_file_id,
            gemini_store_id=store.store_name,
            gemini_mime_type=mime_type,
            gemini_metadata=metadata,
            status="completed",
            error_message=None
        )

        db.add(document)

        # Update store statistics
        store.document_count += 1
        store.total_size_bytes += file_size
        store.updated_at = get_timestamp()

        db.commit()
        db.refresh(document)

        return document

    def delete_document(
        self,
        db: Session,
        document_id: int,
        delete_from_gemini: bool = True
    ) -> bool:
        """
        Delete a document from database and optionally from Gemini

        Args:
            db: Database session
            document_id: Document database ID
            delete_from_gemini: If True, also delete from Gemini API

        Returns:
            True if successful
        """
        document = db.get(Document, document_id)
        if not document:
            return False

        # Delete from Gemini API if requested
        if delete_from_gemini and document.gemini_file_id:
            try:
                self._ensure_client()
                self.client.files.delete(name=document.gemini_file_id)
            except Exception as e:
                print(f"Error deleting from Gemini: {e}")

        # Update store statistics
        if document.gemini_store_id:
            statement = select(GeminiFileSearchStore).where(
                GeminiFileSearchStore.store_name == document.gemini_store_id
            )
            store = db.exec(statement).first()
            if store:
                store.document_count = max(0, store.document_count - 1)
                store.total_size_bytes = max(0, store.total_size_bytes - document.file_size)
                store.updated_at = get_timestamp()

        # Delete from database
        db.delete(document)
        db.commit()

        return True

    def list_documents(
        self,
        db: Session,
        user_id: Optional[int] = None,
        store_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Document]:
        """
        List documents from database

        Args:
            db: Database session
            user_id: Filter by user ID
            store_id: Filter by store database ID
            limit: Max results
            offset: Pagination offset

        Returns:
            List of Document records
        """
        statement = select(Document).order_by(Document.created_at.desc())

        if user_id is not None:
            statement = statement.where(Document.user_id == user_id)

        if store_id is not None:
            store = db.get(GeminiFileSearchStore, store_id)
            if store:
                statement = statement.where(Document.gemini_store_id == store.store_name)

        statement = statement.limit(limit).offset(offset)

        return list(db.exec(statement).all())

    # ===========================
    # RAG Query
    # ===========================

    def query_with_file_search(
        self,
        query: str,
        store_name: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        metadata_filter: Optional[str] = None
    ) -> dict:
        """
        Query using Gemini File Search RAG

        Args:
            query: User query
            store_name: Gemini store resource name (e.g., "fileSearchStores/abc123")
            model: Gemini model to use (gemini-2.5-flash or gemini-2.5-pro)
            temperature: Model temperature
            max_output_tokens: Max tokens in response
            metadata_filter: Optional metadata filter (e.g., "author=Robert Graves")

        Returns:
            Dict with 'content' and 'grounding_metadata' (citations)
        """
        self._ensure_client()

        try:
            # Build file search tool config
            file_search_config = types.FileSearch(
                file_search_store_names=[store_name]
            )

            # Add metadata filter if provided
            if metadata_filter:
                file_search_config.metadata_filter = metadata_filter

            # Create enhanced prompt that instructs model to ONLY use document context
            system_instruction = """You are a helpful assistant that answers questions based STRICTLY on the provided documents.

IMPORTANT INSTRUCTIONS:
1. ONLY use information found in the documents provided via the file search tool
2. If the answer is in the documents, provide a detailed response with direct quotes when relevant
3. If the information is NOT in the documents, clearly state: "I don't have that information in the provided documents"
4. DO NOT use your general knowledge or training data - ONLY use the document content
5. When answering, cite specific information from the documents
6. Be thorough in searching through all available documents before saying information is not available"""

            # Generate content with file search tool
            response = self.client.models.generate_content(
                model=model,
                contents=query,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    tools=[
                        types.Tool(file_search=file_search_config)
                    ]
                )
            )

            # Extract response text
            content = response.text if hasattr(response, 'text') else str(response)

            # Extract grounding metadata (citations)
            grounding_metadata = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    grounding_metadata = candidate.grounding_metadata

            return {
                'content': content,
                'grounding_metadata': grounding_metadata,
                'model': model
            }

        except Exception as e:
            raise RuntimeError(f"Gemini query failed: {str(e)}")

    # ===========================
    # Utility Methods
    # ===========================

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_file_status(self, file_id: str) -> str:
        """
        Get status of a file in Gemini API

        Args:
            file_id: Gemini file ID

        Returns:
            Status string: 'active', 'processing', 'failed'
        """
        self._ensure_client()

        try:
            file = self.client.files.get(name=file_id)
            # Access state as string attribute
            state = str(file.state).upper() if hasattr(file, 'state') else 'UNKNOWN'

            # Map state values to consistent return values
            if 'ACTIVE' in state:
                return 'active'
            elif 'PROCESSING' in state:
                return 'processing'
            elif 'FAILED' in state:
                return 'failed'
            else:
                return 'unknown'

        except Exception as e:
            raise RuntimeError(f"Failed to get file status: {str(e)}")

    def get_store_info(self, store_name: str) -> dict:
        """
        Get information about a file search store from Gemini API

        Args:
            store_name: Gemini store resource name

        Returns:
            Dict with store information
        """
        self._ensure_client()

        try:
            store = self.client.file_search_stores.get(name=store_name)
            return {
                'name': store.name,
                'display_name': store.display_name if hasattr(store, 'display_name') else None,
                'create_time': store.create_time if hasattr(store, 'create_time') else None,
                'update_time': store.update_time if hasattr(store, 'update_time') else None,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get store info: {str(e)}")
