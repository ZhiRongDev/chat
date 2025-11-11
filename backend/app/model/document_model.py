"""
Document models for RAG system using Gemini File Search API
Stores document metadata and Gemini File Search integration
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
    and their Gemini File Search integration
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

    # Gemini File Search fields
    gemini_file_id: Optional[str] = Field(default=None, max_length=255)  # Gemini File API ID
    gemini_store_id: Optional[str] = Field(default=None, max_length=255)  # File Search Store ID
    gemini_mime_type: Optional[str] = Field(default=None, max_length=100)  # MIME type
    gemini_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Gemini custom metadata

    created_at: int = Field(default_factory=get_timestamp)
    updated_at: int = Field(default_factory=get_timestamp)


class GeminiFileSearchStore(SQLModel, table=True):
    """
    Gemini File Search Store configuration
    Tracks File Search Stores for different users or contexts
    """
    __tablename__ = "gemini_file_search_store"

    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    user_id: Optional[int] = Field(
        sa_column=Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=True),
        default=None,
    )
    store_name: str = Field(max_length=255)  # Gemini store resource name (e.g., "file_search_stores/abc123")
    display_name: str = Field(max_length=255)  # User-friendly name
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Statistics
    document_count: int = Field(default=0)
    total_size_bytes: int = Field(default=0)

    is_active: bool = Field(default=True)
    created_at: int = Field(default_factory=get_timestamp)
    updated_at: int = Field(default_factory=get_timestamp)
