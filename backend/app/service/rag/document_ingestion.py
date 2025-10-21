"""
Document Ingestion Service for RAG
Handles document upload, processing, chunking, and indexing
"""

import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any, BinaryIO
from sqlmodel import Session, select
from pypdf import PdfReader
import requests

from app.model import engine
from app.model.document_model import Document, DocumentChunk
from app.service.rag.embedding_service import EmbeddingService
from app.service.rag.vector_store import VectorStoreService


class DocumentIngestionService:
    """
    Service for ingesting documents into the RAG system
    Handles file processing, chunking, embedding, and storage
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        """
        Initialize document ingestion service

        Args:
            embedding_service: Embedding service
            vector_store: Vector store service
            chunk_size: Size of text chunks in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize vector store if not provided
        if vector_store:
            self.vector_store = vector_store
        else:
            self.vector_store = VectorStoreService(
                store_type="faiss",
                store_name="default",
                embedding_dimension=self.embedding_service.get_embedding_dimension(),
            )

    def ingest_file(
        self,
        file: BinaryIO,
        filename: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Ingest a file into the RAG system

        Args:
            file: File-like object (from upload)
            filename: Original filename
            user_id: User ID (optional)
            metadata: Additional metadata

        Returns:
            Created Document object
        """
        # Read file content
        content = file.read()
        file_size = len(content)
        file_type = self._detect_file_type(filename)

        # Compute content hash for deduplication
        content_hash = hashlib.sha256(content).hexdigest()

        # Check for duplicate
        with Session(engine) as session:
            existing = session.exec(
                select(Document).where(
                    Document.content_hash == content_hash,
                    Document.user_id == user_id,
                )
            ).first()

            if existing:
                return existing

            # Create document record
            document = Document(
                user_id=user_id,
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                content_hash=content_hash,
                metadata=metadata or {},
                status="processing",
            )

            session.add(document)
            session.commit()
            session.refresh(document)

            try:
                # Extract text
                text = self._extract_text(content, file_type)

                # Process and index
                self._process_document(document.id, text)

                # Update status
                document.status = "completed"
                session.add(document)
                session.commit()
                session.refresh(document)

            except Exception as e:
                document.status = "failed"
                document.error_message = str(e)
                session.add(document)
                session.commit()
                raise

            return document

    def ingest_text(
        self,
        text: str,
        title: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Ingest raw text into the RAG system

        Args:
            text: Text content
            title: Document title
            user_id: User ID (optional)
            metadata: Additional metadata

        Returns:
            Created Document object
        """
        # Compute hash
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        with Session(engine) as session:
            # Check for duplicate
            existing = session.exec(
                select(Document).where(
                    Document.content_hash == content_hash,
                    Document.user_id == user_id,
                )
            ).first()

            if existing:
                return existing

            # Create document
            document = Document(
                user_id=user_id,
                filename=title,
                file_type="text",
                file_size=len(text.encode("utf-8")),
                content_hash=content_hash,
                extra_metadata=metadata or {},
                status="processing",
            )

            session.add(document)
            session.commit()
            session.refresh(document)

            try:
                self._process_document(document.id, text)

                document.status = "completed"
                session.add(document)
                session.commit()
                session.refresh(document)

            except Exception as e:
                document.status = "failed"
                document.error_message = str(e)
                session.add(document)
                session.commit()
                raise

            return document

    def ingest_url(
        self,
        url: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Ingest content from a URL

        Args:
            url: URL to fetch
            user_id: User ID
            metadata: Additional metadata

        Returns:
            Created Document object
        """
        # Fetch content
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        content = response.text
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        with Session(engine) as session:
            # Check for duplicate
            existing = session.exec(
                select(Document).where(
                    Document.content_hash == content_hash,
                    Document.user_id == user_id,
                )
            ).first()

            if existing:
                return existing

            # Create document
            document = Document(
                user_id=user_id,
                filename=url.split("/")[-1] or "web_page",
                file_type="url",
                file_size=len(content.encode("utf-8")),
                content_hash=content_hash,
                source_url=url,
                extra_metadata=metadata or {},
                status="processing",
            )

            session.add(document)
            session.commit()
            session.refresh(document)

            try:
                # Simple text extraction (could use BeautifulSoup for better HTML parsing)
                text = content

                self._process_document(document.id, text)

                document.status = "completed"
                session.add(document)
                session.commit()
                session.refresh(document)

            except Exception as e:
                document.status = "failed"
                document.error_message = str(e)
                session.add(document)
                session.commit()
                raise

            return document

    def _process_document(self, document_id: int, text: str) -> None:
        """
        Process document: chunk, embed, and store

        Args:
            document_id: Document ID
            text: Extracted text
        """
        # Chunk text
        chunks = self.embedding_service.chunk_text(
            text=text,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        # Generate embeddings (batch)
        embeddings = self.embedding_service.embed_texts(chunks)

        # Store chunks and embeddings
        chunk_ids = []
        with Session(engine) as session:
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                # Compute chunk hash
                chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()

                # Count tokens
                token_count = self.embedding_service.count_tokens(chunk_text)

                # Create chunk record
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=i,
                    content=chunk_text,
                    content_hash=chunk_hash,
                    token_count=token_count,
                    embedding_model=self.embedding_service.model,
                    vector_id=str(document_id) + "_" + str(i),  # Unique ID for vector store
                )

                session.add(chunk)
                session.commit()
                session.refresh(chunk)

                chunk_ids.append(str(chunk.id))

            # Update document chunk count
            document = session.get(Document, document_id)
            if document:
                document.chunk_count = len(chunks)
                session.add(document)
                session.commit()

        # Add to vector store
        self.vector_store.add_embeddings(
            embeddings=embeddings,
            ids=chunk_ids,
            metadatas=[{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))],
        )

    def _extract_text(self, content: bytes, file_type: str) -> str:
        """
        Extract text from file content

        Args:
            content: File bytes
            file_type: File type

        Returns:
            Extracted text
        """
        if file_type == "pdf":
            return self._extract_pdf(content)
        elif file_type in ["txt", "md", "text"]:
            return content.decode("utf-8")
        else:
            # Try UTF-8 decode as fallback
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError(f"Unsupported file type: {file_type}")

    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF bytes"""
        from io import BytesIO

        pdf_file = BytesIO(content)
        reader = PdfReader(pdf_file)

        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text())

        return "\n\n".join(text_parts)

    @staticmethod
    def _detect_file_type(filename: str) -> str:
        """Detect file type from filename"""
        suffix = Path(filename).suffix.lower()
        type_map = {
            ".pdf": "pdf",
            ".txt": "txt",
            ".md": "md",
            ".docx": "docx",
            ".doc": "doc",
        }
        return type_map.get(suffix, "unknown")

    def delete_document(self, document_id: int) -> bool:
        """
        Delete document and all its chunks

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        with Session(engine) as session:
            document = session.get(Document, document_id)
            if not document:
                return False

            # Get chunk IDs for vector store deletion
            chunks = session.exec(
                select(DocumentChunk).where(DocumentChunk.document_id == document_id)
            ).all()

            chunk_ids = [str(chunk.id) for chunk in chunks]

            # Delete from vector store
            if chunk_ids:
                self.vector_store.delete_by_ids(chunk_ids)

            # Delete from database (cascade will handle chunks)
            session.delete(document)
            session.commit()

            return True

    def __repr__(self) -> str:
        return f"DocumentIngestionService(chunk_size={self.chunk_size})"
