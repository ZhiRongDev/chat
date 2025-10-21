"""
RAG (Retrieval-Augmented Generation) Service Package

This package implements a complete RAG pipeline with the following components:

1. Query Preprocessing - Clean and embed user queries
2. Vector Store - FAISS/ChromaDB for semantic search
3. Document Retrieval - Top-k context document retrieval
4. Prompt Building - Construct LLM prompts with context
5. RAG Pipeline - Complete orchestration workflow
6. Document Ingestion - Process and index documents

Usage:
    from app.service.rag import RAGPipeline, DocumentIngestionService

    # Initialize RAG pipeline
    rag = RAGPipeline()

    # Query with RAG
    result = rag.query("What is machine learning?")
    print(result["response"])

    # Ingest documents
    ingestion = DocumentIngestionService()
    doc = ingestion.ingest_text("Machine learning is...", "ML Basics")
"""

from app.service.rag.embedding_service import EmbeddingService
from app.service.rag.vector_store import VectorStoreService
from app.service.rag.query_processor import QueryProcessor
from app.service.rag.retrieval_service import RetrievalService, RetrievalResult
from app.service.rag.prompt_builder import PromptBuilder
from app.service.rag.rag_pipeline import RAGPipeline
from app.service.rag.document_ingestion import DocumentIngestionService

__all__ = [
    "EmbeddingService",
    "VectorStoreService",
    "QueryProcessor",
    "RetrievalService",
    "RetrievalResult",
    "PromptBuilder",
    "RAGPipeline",
    "DocumentIngestionService",
]
