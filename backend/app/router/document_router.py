"""
Document Router for RAG System
Handles document upload, management, and retrieval endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from sqlmodel import Session, select

from app.auth import get_current_user
from app.model.user_model import User
from app.model.document_model import Document, DocumentChunk
from app.model import engine
from app.service.rag import DocumentIngestionService, RAGPipeline


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
    chunk_count: int
    status: str


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
    chunk_count: int
    status: str
    created_at: int
    updated_at: int


class DocumentDetailResponse(BaseModel):
    """Response for document detail with chunks"""
    id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    error_message: Optional[str]
    metadata: Optional[dict]
    created_at: int
    updated_at: int
    chunks: Optional[List[dict]] = None


class DocumentStatsResponse(BaseModel):
    """Response for document statistics"""
    total_documents: int
    total_chunks: int
    total_size_bytes: int
    documents_by_type: dict


# ============================================================================
# Document Ingestion Endpoints (Authenticated)
# ============================================================================


@auth_router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and ingest a document file

    Supported formats: PDF, TXT, MD

    Args:
        file: Document file to upload
        current_user: Authenticated user

    Returns:
        Document upload response with metadata
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    # Check file size (e.g., 10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {max_size} bytes",
        )

    # Reset file pointer
    await file.seek(0)

    try:
        ingestion_service = DocumentIngestionService()
        document = ingestion_service.ingest_file(
            file=file.file,
            filename=file.filename,
            user_id=current_user.id,
        )

        return DocumentUploadResponse(
            id=str(document.id),
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            status=document.status,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}",
        )


@auth_router.post("/ingest/text", response_model=DocumentUploadResponse)
async def ingest_text(
    request: TextIngestionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Ingest text content directly

    Args:
        request: Text ingestion request
        current_user: Authenticated user

    Returns:
        Document upload response
    """
    try:
        ingestion_service = DocumentIngestionService()
        document = ingestion_service.ingest_text(
            text=request.content,
            title=request.title,
            user_id=current_user.id,
            metadata=request.metadata,
        )

        return DocumentUploadResponse(
            id=str(document.id),
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            status=document.status,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest text: {str(e)}",
        )


@auth_router.post("/ingest/url", response_model=DocumentUploadResponse)
async def ingest_url(
    request: URLIngestionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Ingest content from a URL

    Args:
        request: URL ingestion request
        current_user: Authenticated user

    Returns:
        Document upload response
    """
    try:
        ingestion_service = DocumentIngestionService()
        document = ingestion_service.ingest_url(
            url=str(request.url),
            user_id=current_user.id,
            metadata=request.metadata,
        )

        return DocumentUploadResponse(
            id=str(document.id),
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            status=document.status,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest URL: {str(e)}",
        )


# ============================================================================
# Document Management Endpoints (Authenticated)
# ============================================================================


@auth_router.get("/", response_model=List[DocumentListResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
):
    """
    List all documents for authenticated user

    Args:
        current_user: Authenticated user
        limit: Maximum number of documents to return
        offset: Offset for pagination

    Returns:
        List of documents
    """
    with Session(engine) as session:
        statement = (
            select(Document)
            .where(Document.user_id == current_user.id)
            .offset(offset)
            .limit(limit)
            .order_by(Document.created_at.desc())
        )

        documents = session.exec(statement).all()

        return [
            DocumentListResponse(
                id=str(doc.id),
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                chunk_count=doc.chunk_count,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in documents
        ]


@auth_router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    include_chunks: bool = False,
):
    """
    Get document details

    Args:
        document_id: Document ID
        current_user: Authenticated user
        include_chunks: Whether to include chunk content

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

    with Session(engine) as session:
        document = session.get(Document, doc_id_int)

        if not document or document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        chunks_data = None
        if include_chunks:
            chunks = session.exec(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == doc_id_int)
                .order_by(DocumentChunk.chunk_index)
            ).all()

            chunks_data = [
                {
                    "id": str(chunk.id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "token_count": chunk.token_count,
                }
                for chunk in chunks
            ]

        return DocumentDetailResponse(
            id=str(document.id),
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            status=document.status,
            error_message=document.error_message,
            metadata=document.extra_metadata,
            created_at=document.created_at,
            updated_at=document.updated_at,
            chunks=chunks_data,
        )


@auth_router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document and all its chunks

    Args:
        document_id: Document ID
        current_user: Authenticated user

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

    # Verify ownership
    with Session(engine) as session:
        document = session.get(Document, doc_id_int)

        if not document or document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

    # Delete using ingestion service
    try:
        ingestion_service = DocumentIngestionService()
        deleted = ingestion_service.delete_document(doc_id_int)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return {"detail": "Document deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )


@auth_router.get("/stats/overview", response_model=DocumentStatsResponse)
async def get_document_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get document statistics for user

    Args:
        current_user: Authenticated user

    Returns:
        Document statistics
    """
    with Session(engine) as session:
        documents = session.exec(
            select(Document).where(Document.user_id == current_user.id)
        ).all()

        total_documents = len(documents)
        total_chunks = sum(doc.chunk_count for doc in documents)
        total_size = sum(doc.file_size for doc in documents)

        # Count by type
        type_counts = {}
        for doc in documents:
            type_counts[doc.file_type] = type_counts.get(doc.file_type, 0) + 1

        return DocumentStatsResponse(
            total_documents=total_documents,
            total_chunks=total_chunks,
            total_size_bytes=total_size,
            documents_by_type=type_counts,
        )
