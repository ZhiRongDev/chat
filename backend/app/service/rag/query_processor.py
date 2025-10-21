"""
Query Preprocessing Service for RAG
Handles query cleaning, expansion, and embedding
"""

import re
from typing import List, Optional
from app.service.rag.embedding_service import EmbeddingService


class QueryProcessor:
    """
    Service for preprocessing user queries before retrieval
    Handles cleaning, normalization, and embedding generation
    """

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        """
        Initialize query processor

        Args:
            embedding_service: Embedding service for query embedding
        """
        self.embedding_service = embedding_service or EmbeddingService()

    def clean_query(self, query: str) -> str:
        """
        Clean and normalize query text

        Args:
            query: Raw query text

        Returns:
            Cleaned query text
        """
        # Remove extra whitespace
        query = re.sub(r"\s+", " ", query).strip()

        # Remove special characters but keep punctuation
        # This preserves question marks, periods, etc.
        query = re.sub(r"[^\w\s\?\.\!\,\-]", "", query)

        return query

    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with synonyms or related terms (optional enhancement)

        Args:
            query: Original query

        Returns:
            List of query variations (currently just returns original)
        """
        # Basic implementation - could be enhanced with:
        # - Synonym expansion using WordNet
        # - Query reformulation using LLM
        # - Common abbreviation expansion
        return [query]

    def preprocess(self, query: str) -> str:
        """
        Full preprocessing pipeline

        Args:
            query: Raw query text

        Returns:
            Preprocessed query
        """
        # Clean the query
        cleaned = self.clean_query(query)

        # Could add more preprocessing steps:
        # - Spell correction
        # - Language detection
        # - Query intent classification

        return cleaned

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for query

        Args:
            query: Query text

        Returns:
            Query embedding vector
        """
        # Preprocess before embedding
        processed_query = self.preprocess(query)

        # Generate embedding
        return self.embedding_service.embed_text(processed_query)

    def process_and_embed(self, query: str) -> tuple[str, List[float]]:
        """
        Complete pipeline: preprocess and embed query

        Args:
            query: Raw query text

        Returns:
            Tuple of (processed_query, embedding)
        """
        processed = self.preprocess(query)
        embedding = self.embedding_service.embed_text(processed)
        return processed, embedding

    @staticmethod
    def extract_keywords(query: str, top_k: int = 5) -> List[str]:
        """
        Extract keywords from query (simple implementation)

        Args:
            query: Query text
            top_k: Number of keywords to extract

        Returns:
            List of keywords
        """
        # Simple word extraction (could be enhanced with NLP)
        words = query.lower().split()

        # Remove common stop words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "should", "could", "may", "might", "can", "what",
            "when", "where", "who", "which", "why", "how", "in", "on",
            "at", "to", "for", "of", "with", "by", "from", "and", "or",
            "but", "not", "if", "then", "than"
        }

        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords[:top_k]

    def __repr__(self) -> str:
        return f"QueryProcessor(embedding_service={self.embedding_service})"
