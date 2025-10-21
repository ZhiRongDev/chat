"""
Document models for RAG system
Stores document metadata, chunks, and embeddings information
"""

from sqlmodel import SQLModel, Field, Column, Relationship
from app.utils import snowflake_generator, get_timestamp
from sqlalchemy import BigInteger, ForeignKey, Text, JSON
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.model.user_model import User


class Document(SQLModel, table=True):
    """
    Document metadata - stores information about uploaded documents
    """
    __tablename__ = "document"

    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    user_id: Optional[int] = Field(
        sa_column=Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=True),
        default=None,
    )
    filename: str = Field(max_length=255)
    file_type: str = Field(max_length=50)  # pdf, txt, md, docx, etc.
    file_size: int  # Size in bytes
    content_hash: str = Field(max_length=64)  # SHA-256 hash for deduplication
    source_url: Optional[str] = Field(default=None, max_length=500)  # If from URL
    extra_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Custom metadata
    status: str = Field(default="pending", max_length=20)  # pending, processing, completed, failed
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    chunk_count: int = Field(default=0)  # Number of chunks created
    created_at: int = Field(default_factory=get_timestamp)
    updated_at: int = Field(default_factory=get_timestamp)

    # Relationships
    chunks: list["DocumentChunk"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class DocumentChunk(SQLModel, table=True):
    """
    Document chunks - stores text chunks with embedding metadata
    Each chunk represents a segment of text from a document that can be retrieved
    """
    __tablename__ = "document_chunk"

    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    document_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("document.id", ondelete="CASCADE"))
    )
    chunk_index: int  # Order within the document (0-indexed)
    content: str = Field(sa_column=Column(Text))  # The actual text content
    content_hash: str = Field(max_length=64)  # SHA-256 hash for deduplication
    token_count: int  # Number of tokens in this chunk

    # Embedding information
    embedding_model: str = Field(max_length=100)  # e.g., "text-embedding-3-small"
    vector_id: str = Field(max_length=255)  # ID in the vector store (FAISS/ChromaDB)

    # Metadata for enhanced retrieval
    extra_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    created_at: int = Field(default_factory=get_timestamp)

    # Relationships
    document: Optional[Document] = Relationship(back_populates="chunks")


class VectorStoreConfig(SQLModel, table=True):
    """
    Configuration for vector stores
    Tracks different vector store instances and their configurations
    """
    __tablename__ = "vector_store_config"

    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    name: str = Field(max_length=100, unique=True)  # e.g., "default", "user_123"
    store_type: str = Field(max_length=50)  # faiss, chromadb
    embedding_model: str = Field(max_length=100)
    embedding_dimension: int  # Dimension of embeddings (e.g., 1536 for OpenAI)
    distance_metric: str = Field(default="cosine", max_length=20)  # cosine, euclidean, dot

    # Store-specific configuration
    config: dict = Field(sa_column=Column(JSON))

    # Statistics
    document_count: int = Field(default=0)
    chunk_count: int = Field(default=0)

    is_active: bool = Field(default=True)
    created_at: int = Field(default_factory=get_timestamp)
    updated_at: int = Field(default_factory=get_timestamp)
