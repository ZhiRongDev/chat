"""
Document Router for Gemini File Search RAG System
Handles document upload, management, and retrieval using Gemini File Search API
"""

import os
import tempfile
import requests
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Header
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from sqlmodel import Session

from app.auth import get_current_user
from app.model.user_model import User
from app.model.document_model import Document
import app.model
from app.service.gemini_file_search_service import GeminiFileSearchService
from app.service.document_sync_service import DocumentSyncService
from app.config import settings


# Routers
nonauth_router = APIRouter(prefix="/documents", tags=["documents"])
auth_router = APIRouter(prefix="/documents", tags=["documents"])


# Request/Response Models
class DocumentUploadResponse(BaseModel):
    """Response for document upload"""

    id: str  # Snowflake ID as string
    filename: str
    file_type: str
    file_size: int
    status: str
    gemini_file_id: Optional[str] = None


class TextIngestionRequest(BaseModel):
    """Request for ingesting text content"""

    title: str
    content: str
    metadata: Optional[dict] = None


class URLIngestionRequest(BaseModel):
    """Request for ingesting content from URL"""

    url: HttpUrl
    metadata: Optional[dict] = None


class DocumentListResponse(BaseModel):
    """Response for document list"""

    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    gemini_file_id: Optional[str]
    created_at: int
    updated_at: int


class DocumentDetailResponse(BaseModel):
    """Response for document detail"""

    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str]
    metadata: Optional[dict]
    gemini_file_id: Optional[str]
    gemini_store_id: Optional[str]
    gemini_metadata: Optional[dict]
    created_at: int
    updated_at: int


class DocumentStatsResponse(BaseModel):
    """Response for document statistics"""

    total_documents: int
    total_size_bytes: int
    documents_by_type: dict


class StoreInfoResponse(BaseModel):
    """Response for File Search Store information"""

    id: str
    display_name: str
    description: Optional[str]
    document_count: int
    total_size_bytes: int
    created_at: int
    api_key_identifier: str  # First 8 chars of API key hash for identification


# ============================================================================
# Document Ingestion Endpoints (Authenticated)
# ============================================================================


@auth_router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    x_gemini_api_key: Optional[str] = Header(None),
):
    """
    Upload and ingest a document file to Gemini File Search

    Supported formats: PDF, TXT, MD, DOCX, and more (see Gemini docs)

    Args:
        file: Document file to upload
        current_user: Authenticated user
        x_gemini_api_key: Optional Gemini API key via header (overrides server config)

    Returns:
        Document upload response with metadata
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    # Check file size
    max_size = settings.GEMINI_MAX_FILE_SIZE_MB * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {settings.GEMINI_MAX_FILE_SIZE_MB}MB limit",
        )

    # Create temporary file
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(file.filename).suffix
    ) as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = tmp_file.name

    try:
        # Use user-provided API key if available, otherwise use server config
        gemini_service = GeminiFileSearchService(api_key=x_gemini_api_key)

        with Session(app.model.engine) as session:
            # Get or create user's file search store
            store = gemini_service.get_or_create_user_store(session, current_user.id)

            # Upload to Gemini
            document = gemini_service.upload_file_to_store(
                db=session,
                file_path=tmp_file_path,
                store_id=store.id,
                filename=file.filename,
                user_id=current_user.id,
                metadata={"uploaded_by": str(current_user.id)},
            )

            return DocumentUploadResponse(
                id=str(document.id),
                filename=document.filename,
                file_type=document.file_type,
                file_size=document.file_size,
                status=document.status,
                gemini_file_id=document.gemini_file_id,
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@auth_router.post("/ingest/text", response_model=DocumentUploadResponse)
async def ingest_text(
    request: TextIngestionRequest,
    current_user: User = Depends(get_current_user),
    x_gemini_api_key: Optional[str] = Header(None),
):
    """
    Ingest text content directly by creating a temporary file

    Args:
        request: Text ingestion request
        current_user: Authenticated user
        x_gemini_api_key: Optional Gemini API key via header (overrides server config)

    Returns:
        Document upload response
    """
    # Create temporary file with text content
    filename = f"{request.title}.txt"
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp_file:
        tmp_file.write(request.content)
        tmp_file_path = tmp_file.name

    try:
        # Use user-provided API key if available, otherwise use server config
        gemini_service = GeminiFileSearchService(api_key=x_gemini_api_key)

        with Session(app.model.engine) as session:
            # Get or create user's file search store
            store = gemini_service.get_or_create_user_store(session, current_user.id)

            # Upload to Gemini
            metadata = request.metadata or {}
            metadata.update(
                {"type": "text_ingestion", "uploaded_by": str(current_user.id)}
            )

            document = gemini_service.upload_file_to_store(
                db=session,
                file_path=tmp_file_path,
                store_id=store.id,
                filename=filename,
                user_id=current_user.id,
                metadata=metadata,
            )

            return DocumentUploadResponse(
                id=str(document.id),
                filename=document.filename,
                file_type=document.file_type,
                file_size=document.file_size,
                status=document.status,
                gemini_file_id=document.gemini_file_id,
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest text: {str(e)}",
        )
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@auth_router.post("/ingest/url", response_model=DocumentUploadResponse)
async def ingest_url(
    request: URLIngestionRequest,
    current_user: User = Depends(get_current_user),
    x_gemini_api_key: Optional[str] = Header(None),
):
    """
    Ingest content from a URL by downloading and uploading to Gemini

    Args:
        request: URL ingestion request
        current_user: Authenticated user
        x_gemini_api_key: Optional Gemini API key via header (overrides server config)

    Returns:
        Document upload response
    """
    try:
        # Download content from URL
        response = requests.get(str(request.url), timeout=30)
        response.raise_for_status()

        # Determine filename from URL
        url_path = Path(str(request.url))
        filename = url_path.name or "downloaded_content.txt"

        # Create temporary file
        suffix = url_path.suffix or ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name

    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to download from URL: {str(e)}",
        )

    try:
        # Use user-provided API key if available, otherwise use server config
        gemini_service = GeminiFileSearchService(api_key=x_gemini_api_key)

        with Session(app.model.engine) as session:
            # Get or create user's file search store
            store = gemini_service.get_or_create_user_store(session, current_user.id)

            # Upload to Gemini
            metadata = request.metadata or {}
            metadata.update(
                {
                    "type": "url_ingestion",
                    "uploaded_by": str(current_user.id),
                    "source_url": str(request.url),
                }
            )

            document = gemini_service.upload_file_to_store(
                db=session,
                file_path=tmp_file_path,
                store_id=store.id,
                filename=filename,
                user_id=current_user.id,
                metadata=metadata,
                source_url=str(request.url),
            )

            return DocumentUploadResponse(
                id=str(document.id),
                filename=document.filename,
                file_type=document.file_type,
                file_size=document.file_size,
                status=document.status,
                gemini_file_id=document.gemini_file_id,
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest URL: {str(e)}",
        )
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


# ============================================================================
# Document Management Endpoints (Authenticated)
# ============================================================================


@auth_router.get("/", response_model=List[DocumentListResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    x_gemini_api_key: Optional[str] = Header(None),
    limit: int = 100,
    offset: int = 0,
    sync: bool = True,  # Enable auto-sync by default
):
    """
    List all documents for authenticated user in the current API key's store

    Args:
        current_user: Authenticated user
        x_gemini_api_key: Optional Gemini API key via header (filters by this key's store)
        limit: Maximum number of documents to return
        offset: Offset for pagination
        sync: If True, automatically sync with Gemini before returning (default: True)

    Returns:
        List of documents from the current API key's store
    """
    import logging

    logger = logging.getLogger(__name__)

    # Use user-provided API key if available, otherwise use server config
    gemini_service = GeminiFileSearchService(api_key=x_gemini_api_key)

    logger.info(
        f"list_documents: user_id={current_user.id}, has_api_key_header={bool(x_gemini_api_key)}, api_key_hash={gemini_service.api_key_hash[:8] if gemini_service.api_key_hash else 'None'}, sync={sync}"
    )

    with Session(app.model.engine) as session:
        # Get the user's store for the current API key
        store = gemini_service.get_or_create_user_store(session, current_user.id)

        logger.info(
            f"  Found/created store: id={store.id}, store_name={store.store_name}, api_key_hash={store.api_key_hash[:8] if store.api_key_hash else 'None'}, is_active={store.is_active}, document_count={store.document_count}"
        )

        # Auto-sync with Gemini if requested
        if sync and gemini_service.client:
            try:
                sync_service = DocumentSyncService(
                    gemini_client=gemini_service.client,
                    api_key_hash=gemini_service.api_key_hash
                )
                added, removed = sync_service.sync_store_documents(session, store)
                if added > 0 or removed > 0:
                    logger.info(f"  Auto-sync: {added} documents added, {removed} removed")
            except Exception as e:
                logger.error(f"  Auto-sync failed (continuing with database query): {e}")

        # List documents from this specific store
        documents = gemini_service.list_documents(
            db=session,
            user_id=current_user.id,
            store_id=store.id,
            limit=limit,
            offset=offset,
        )

        logger.info(f"  Retrieved {len(documents)} documents from database")

        return [
            DocumentListResponse(
                id=str(doc.id),
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                status=doc.status,
                gemini_file_id=doc.gemini_file_id,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in documents
        ]


@auth_router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get document details

    Args:
        document_id: Document ID
        current_user: Authenticated user

    Returns:
        Document details
    """
    try:
        doc_id_int = int(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document_id format",
        )

    with Session(app.model.engine) as session:
        document = session.get(Document, doc_id_int)

        if not document or document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return DocumentDetailResponse(
            id=str(document.id),
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            status=document.status,
            error_message=document.error_message,
            metadata=document.extra_metadata,
            gemini_file_id=document.gemini_file_id,
            gemini_store_id=document.gemini_store_id,
            gemini_metadata=document.gemini_metadata,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


@auth_router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    x_gemini_api_key: Optional[str] = Header(None),
):
    """
    Delete a document from Gemini File Search and database

    Args:
        document_id: Document ID
        current_user: Authenticated user
        x_gemini_api_key: Optional Gemini API key via header (overrides server config)

    Returns:
        Success message
    """
    try:
        doc_id_int = int(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document_id format",
        )

    # Use user-provided API key if available, otherwise use server config
    gemini_service = GeminiFileSearchService(api_key=x_gemini_api_key)

    with Session(app.model.engine) as session:
        # Verify ownership
        document = session.get(Document, doc_id_int)

        if not document or document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Delete document (deletes from both Gemini and database)
        try:
            deleted = gemini_service.delete_document(
                db=session, document_id=doc_id_int, delete_from_gemini=True
            )

            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found",
                )

            return {"detail": "Document deleted successfully from Gemini and database"}

        except RuntimeError as e:
            # Gemini deletion failed - document remains in both places
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document from Gemini File Search: {str(e)}. Document has not been deleted.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document: {str(e)}",
            )


@auth_router.get("/stats/overview", response_model=DocumentStatsResponse)
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    x_gemini_api_key: Optional[str] = Header(None),
):
    """
    Get document statistics for user in the current API key's store

    Args:
        current_user: Authenticated user
        x_gemini_api_key: Optional Gemini API key via header (filters by this key's store)

    Returns:
        Document statistics from the current API key's store
    """
    # Use user-provided API key if available, otherwise use server config
    gemini_service = GeminiFileSearchService(api_key=x_gemini_api_key)

    with Session(app.model.engine) as session:
        # Get the user's store for the current API key
        store = gemini_service.get_or_create_user_store(session, current_user.id)

        # Get documents from this specific store
        documents = gemini_service.list_documents(
            db=session,
            user_id=current_user.id,
            store_id=store.id,
            limit=10000,  # Get all for stats
        )

        total_documents = len(documents)
        total_size = sum(doc.file_size for doc in documents)

        # Count by type
        type_counts = {}
        for doc in documents:
            type_counts[doc.file_type] = type_counts.get(doc.file_type, 0) + 1

        return DocumentStatsResponse(
            total_documents=total_documents,
            total_size_bytes=total_size,
            documents_by_type=type_counts,
        )


# ============================================================================
# File Search Store Management (Authenticated)
# ============================================================================


@auth_router.get("/stores/info", response_model=StoreInfoResponse)
async def get_user_store_info(
    current_user: User = Depends(get_current_user),
    x_gemini_api_key: Optional[str] = Header(None),
):
    """
    Get information about user's File Search Store

    Args:
        current_user: Authenticated user
        x_gemini_api_key: Optional Gemini API key via header (overrides server config)

    Returns:
        Store information
    """
    # Use user-provided API key if available, otherwise use server config
    gemini_service = GeminiFileSearchService(api_key=x_gemini_api_key)

    with Session(app.model.engine) as session:
        store = gemini_service.get_or_create_user_store(session, current_user.id)

        return StoreInfoResponse(
            id=str(store.id),
            display_name=store.display_name,
            description=store.description,
            document_count=store.document_count,
            total_size_bytes=store.total_size_bytes,
            created_at=store.created_at,
            api_key_identifier=(
                store.api_key_hash[:8] if store.api_key_hash else "unknown"
            ),
        )
