"""
Embedding Service for RAG
Handles text embedding generation using various providers
"""

import hashlib
import tiktoken
from typing import List, Optional, Literal
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings
from app.config import settings


EmbeddingProvider = Literal["openai", "google"]


class EmbeddingService:
    """
    Service for generating text embeddings
    Supports multiple embedding providers (OpenAI, Google)
    """

    # Default embedding models for each provider
    DEFAULT_MODELS = {
        "openai": "text-embedding-3-small",  # 1536 dimensions, cost-effective
        "google": "models/embedding-001",  # 768 dimensions
    }

    DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
        "models/embedding-001": 768,
    }

    def __init__(
        self,
        provider: Optional[EmbeddingProvider] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize embedding service

        Args:
            provider: Embedding provider (openai, google)
            model: Specific model name (uses default if not specified)
        """
        self.provider = provider or self._get_default_provider()
        self.model = model or self.DEFAULT_MODELS[self.provider]
        self.embeddings = self._create_embeddings()

    @staticmethod
    def _get_default_provider() -> EmbeddingProvider:
        """Determine default provider based on available API keys"""
        if settings.OPENAI_API_KEY:
            return "openai"
        elif settings.GEMINI_API_KEY:
            return "google"
        else:
            raise ValueError("No embedding provider API key found")

    def _create_embeddings(self) -> Embeddings:
        """Create embeddings instance based on provider"""
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            return OpenAIEmbeddings(
                model=self.model,
                api_key=settings.OPENAI_API_KEY,
            )
        elif self.provider == "google":
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            return GoogleGenerativeAIEmbeddings(
                model=self.model,
                google_api_key=settings.GEMINI_API_KEY,
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        return self.embeddings.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for current model"""
        return self.DIMENSIONS.get(self.model, 1536)

    @staticmethod
    def compute_hash(text: str) -> str:
        """
        Compute SHA-256 hash of text for deduplication

        Args:
            text: Text to hash

        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Count tokens in text using tiktoken

        Args:
            text: Text to count tokens for
            model: Model name for tokenizer (default: gpt-3.5-turbo)

        Returns:
            Number of tokens
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        model: str = "gpt-3.5-turbo",
    ) -> List[str]:
        """
        Split text into chunks based on token count

        Args:
            text: Text to chunk
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap between chunks
            model: Model for tokenization

        Returns:
            List of text chunks
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens = encoding.encode(text)
        chunks = []

        start = 0
        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Move start forward with overlap
            start = end - chunk_overlap
            if start >= len(tokens):
                break

        return chunks

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available embedding providers based on API keys"""
        providers = []
        if settings.OPENAI_API_KEY:
            providers.append("openai")
        if settings.GEMINI_API_KEY:
            providers.append("google")
        return providers

    def __repr__(self) -> str:
        return f"EmbeddingService(provider={self.provider}, model={self.model})"
