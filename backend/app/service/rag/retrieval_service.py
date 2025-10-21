"""
Retrieval Service for RAG
Handles semantic search and document retrieval from vector store
"""

from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from app.model import engine
from app.model.document_model import Document, DocumentChunk
from app.service.rag.vector_store import VectorStoreService
from app.service.rag.query_processor import QueryProcessor


class RetrievalResult:
    """Container for retrieval results"""

    def __init__(
        self,
        chunk_id: str,
        document_id: int,
        content: str,
        score: float,
        metadata: Optional[Dict[str, Any]] = None,
        document_title: Optional[str] = None,
        chunk_index: Optional[int] = None,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.score = score
        self.metadata = metadata or {}
        self.document_title = document_title
        self.chunk_index = chunk_index

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "document_title": self.document_title,
            "chunk_index": self.chunk_index,
        }

    def __repr__(self) -> str:
        return f"RetrievalResult(doc={self.document_id}, score={self.score:.3f})"


class RetrievalService:
    """
    Service for retrieving relevant documents from vector store
    Implements semantic search with top-k retrieval
    """

    def __init__(
        self,
        vector_store: VectorStoreService,
        query_processor: Optional[QueryProcessor] = None,
    ):
        """
        Initialize retrieval service

        Args:
            vector_store: Vector store service instance
            query_processor: Query processor (creates default if not provided)
        """
        self.vector_store = vector_store
        self.query_processor = query_processor or QueryProcessor()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve top-k most relevant document chunks for a query

        Args:
            query: User query text
            top_k: Number of results to return
            min_score: Minimum similarity score threshold
            filters: Optional filters (e.g., document_id, user_id)

        Returns:
            List of RetrievalResult objects sorted by relevance
        """
        # Preprocess and embed query
        processed_query, query_embedding = self.query_processor.process_and_embed(query)

        # Search vector store
        search_results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            k=top_k * 2,  # Get more results to allow for filtering
        )

        # Retrieve chunk details from database
        results = []
        with Session(engine) as session:
            for chunk_id, score in search_results:
                # Skip results below threshold
                if score < min_score:
                    continue

                # Get chunk from database
                try:
                    chunk_id_int = int(chunk_id)
                except ValueError:
                    continue

                chunk = session.get(DocumentChunk, chunk_id_int)
                if not chunk:
                    continue

                # Apply filters if provided
                if filters:
                    if filters.get("document_id") and chunk.document_id != filters["document_id"]:
                        continue
                    # Add more filter logic as needed

                # Get document information
                document = session.get(Document, chunk.document_id)
                document_title = document.filename if document else "Unknown"

                # Create result
                result = RetrievalResult(
                    chunk_id=chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=score,
                    metadata=chunk.extra_metadata,
                    document_title=document_title,
                    chunk_index=chunk.chunk_index,
                )
                results.append(result)

                # Stop if we have enough results
                if len(results) >= top_k:
                    break

        return results

    def retrieve_with_context(
        self,
        query: str,
        top_k: int = 5,
        context_chunks: int = 1,
    ) -> List[RetrievalResult]:
        """
        Retrieve documents with surrounding context chunks

        Args:
            query: User query text
            top_k: Number of primary results
            context_chunks: Number of surrounding chunks to include

        Returns:
            List of results with context
        """
        # Get primary results
        primary_results = self.retrieve(query, top_k)

        if context_chunks == 0:
            return primary_results

        # Expand with context
        expanded_results = []
        with Session(engine) as session:
            for result in primary_results:
                # Add the main chunk
                expanded_results.append(result)

                # Get surrounding chunks
                statement = select(DocumentChunk).where(
                    DocumentChunk.document_id == result.document_id,
                    DocumentChunk.chunk_index >= result.chunk_index - context_chunks,
                    DocumentChunk.chunk_index <= result.chunk_index + context_chunks,
                    DocumentChunk.id != int(result.chunk_id),
                ).order_by(DocumentChunk.chunk_index)

                context = session.exec(statement).all()

                for chunk in context:
                    expanded_results.append(
                        RetrievalResult(
                            chunk_id=str(chunk.id),
                            document_id=chunk.document_id,
                            content=chunk.content,
                            score=result.score * 0.8,  # Lower score for context
                            metadata=chunk.extra_metadata,
                            chunk_index=chunk.chunk_index,
                        )
                    )

        return expanded_results

    def retrieve_by_document(
        self,
        document_id: int,
        query: Optional[str] = None,
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """
        Retrieve chunks from a specific document

        Args:
            document_id: Document ID to retrieve from
            query: Optional query for ranking (if None, returns all chunks)
            top_k: Number of results

        Returns:
            List of retrieval results
        """
        if query:
            # Use semantic search within document
            return self.retrieve(
                query=query,
                top_k=top_k,
                filters={"document_id": document_id},
            )
        else:
            # Return all chunks in order
            with Session(engine) as session:
                statement = select(DocumentChunk).where(
                    DocumentChunk.document_id == document_id
                ).order_by(DocumentChunk.chunk_index).limit(top_k)

                chunks = session.exec(statement).all()

                document = session.get(Document, document_id)
                document_title = document.filename if document else "Unknown"

                return [
                    RetrievalResult(
                        chunk_id=str(chunk.id),
                        document_id=chunk.document_id,
                        content=chunk.content,
                        score=1.0,
                        metadata=chunk.extra_metadata,
                        document_title=document_title,
                        chunk_index=chunk.chunk_index,
                    )
                    for chunk in chunks
                ]

    def get_similar_chunks(
        self,
        chunk_id: str,
        top_k: int = 5,
    ) -> List[RetrievalResult]:
        """
        Find similar chunks to a given chunk

        Args:
            chunk_id: ID of reference chunk
            top_k: Number of similar chunks to return

        Returns:
            List of similar chunks
        """
        with Session(engine) as session:
            try:
                chunk_id_int = int(chunk_id)
            except ValueError:
                return []

            chunk = session.get(DocumentChunk, chunk_id_int)
            if not chunk:
                return []

            # Use chunk content as query
            return self.retrieve(query=chunk.content, top_k=top_k + 1)[1:]  # Exclude self

    def __repr__(self) -> str:
        return f"RetrievalService(vector_store={self.vector_store})"
