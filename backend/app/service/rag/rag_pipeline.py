"""
RAG Pipeline Orchestrator
Coordinates the complete RAG workflow from query to response
"""

from typing import List, Optional, AsyncIterator, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.service.rag.embedding_service import EmbeddingService
from app.service.rag.vector_store import VectorStoreService
from app.service.rag.query_processor import QueryProcessor
from app.service.rag.retrieval_service import RetrievalService, RetrievalResult
from app.service.rag.prompt_builder import PromptBuilder
from app.service.llm.llm_factory import get_llm, LLMProvider


class RAGPipeline:
    """
    Complete RAG pipeline orchestrator
    Implements the full workflow: Query → Preprocessing → Retrieval → Prompt Building → LLM
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None,
        query_processor: Optional[QueryProcessor] = None,
        retrieval_service: Optional[RetrievalService] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        llm_provider: Optional[LLMProvider] = None,
        llm_model: Optional[str] = None,
        llm_temperature: float = 0.7,
        top_k: int = 5,
        min_score: float = 0.3,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
    ):
        """
        Initialize RAG pipeline

        Args:
            embedding_service: Service for embeddings
            vector_store: Vector store service
            query_processor: Query preprocessing service
            retrieval_service: Document retrieval service
            prompt_builder: Prompt building service
            llm_provider: LLM provider (gemini, openai, anthropic)
            llm_model: Specific LLM model
            llm_temperature: LLM temperature
            top_k: Number of documents to retrieve
            min_score: Minimum relevance score
            gemini_api_key: User-provided Gemini API key
            openai_api_key: User-provided OpenAI API key
            anthropic_api_key: User-provided Anthropic API key
        """
        # Initialize services
        self.embedding_service = embedding_service or EmbeddingService(
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
        )
        self.query_processor = query_processor or QueryProcessor(self.embedding_service)

        # Vector store
        if vector_store:
            self.vector_store = vector_store
        else:
            # Create default FAISS store
            self.vector_store = VectorStoreService(
                store_type="faiss",
                store_name="default",
                embedding_dimension=self.embedding_service.get_embedding_dimension(),
            )

        # Retrieval and prompt services
        self.retrieval_service = retrieval_service or RetrievalService(
            vector_store=self.vector_store,
            query_processor=self.query_processor,
        )
        self.prompt_builder = prompt_builder or PromptBuilder()

        # LLM configuration
        self.llm = get_llm(
            provider=llm_provider,
            model=llm_model,
            temperature=llm_temperature,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
        )

        # Retrieval configuration
        self.top_k = top_k
        self.min_score = min_score

    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute complete RAG pipeline (synchronous)

        Args:
            query: User query
            top_k: Number of documents to retrieve (overrides default)
            min_score: Minimum score threshold (overrides default)
            filters: Optional filters for retrieval

        Returns:
            Dictionary with response and metadata
        """
        # Use provided values or defaults
        k = top_k or self.top_k
        score = min_score or self.min_score

        # Step 1: Query Preprocessing
        processed_query = self.query_processor.preprocess(query)

        # Step 2: Retrieval
        results = self.retrieval_service.retrieve(
            query=processed_query,
            top_k=k,
            min_score=score,
            filters=filters,
        )

        # Step 3: Prompt Building
        messages = self.prompt_builder.build_messages(query, results)

        # Step 4: LLM Generation
        # Convert to LangChain messages
        langchain_messages = [
            SystemMessage(content=msg["content"])
            if msg["role"] == "system"
            else HumanMessage(content=msg["content"])
            for msg in messages
        ]

        response = self.llm.invoke(langchain_messages)

        # Step 5: Add citations
        response_text = response.content if hasattr(response, "content") else str(response)
        response_with_citations = self.prompt_builder.add_citations(response_text, results)

        return {
            "response": response_with_citations,
            "query": query,
            "processed_query": processed_query,
            "retrieved_documents": [r.to_dict() for r in results],
            "document_count": len(results),
        }

    async def aquery(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute complete RAG pipeline (asynchronous)

        Args:
            query: User query
            top_k: Number of documents to retrieve
            min_score: Minimum score threshold
            filters: Optional filters

        Returns:
            Dictionary with response and metadata
        """
        # Use provided values or defaults
        k = top_k or self.top_k
        score = min_score or self.min_score

        # Preprocessing and retrieval (synchronous for now)
        processed_query = self.query_processor.preprocess(query)
        results = self.retrieval_service.retrieve(
            query=processed_query,
            top_k=k,
            min_score=score,
            filters=filters,
        )

        # Build prompt
        messages = self.prompt_builder.build_messages(query, results)

        # Convert to LangChain messages
        langchain_messages = [
            SystemMessage(content=msg["content"])
            if msg["role"] == "system"
            else HumanMessage(content=msg["content"])
            for msg in messages
        ]

        # Async LLM call
        response = await self.llm.ainvoke(langchain_messages)

        response_text = response.content if hasattr(response, "content") else str(response)
        response_with_citations = self.prompt_builder.add_citations(response_text, results)

        return {
            "response": response_with_citations,
            "query": query,
            "processed_query": processed_query,
            "retrieved_documents": [r.to_dict() for r in results],
            "document_count": len(results),
        }

    async def astream(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        Stream RAG response

        Args:
            query: User query
            top_k: Number of documents to retrieve
            min_score: Minimum score threshold
            filters: Optional filters

        Yields:
            Response chunks
        """
        # Use provided values or defaults
        k = top_k or self.top_k
        score = min_score or self.min_score

        # Preprocessing and retrieval
        processed_query = self.query_processor.preprocess(query)
        results = self.retrieval_service.retrieve(
            query=processed_query,
            top_k=k,
            min_score=score,
            filters=filters,
        )

        # Build prompt
        messages = self.prompt_builder.build_messages(query, results)

        # Convert to LangChain messages
        langchain_messages = [
            SystemMessage(content=msg["content"])
            if msg["role"] == "system"
            else HumanMessage(content=msg["content"])
            for msg in messages
        ]

        # Stream response
        async for chunk in self.llm.astream(langchain_messages):
            if hasattr(chunk, "content"):
                yield chunk.content

        # Add citations at the end
        if results:
            citations = self.prompt_builder.add_citations("", results)
            # Extract just the sources part
            sources = citations.replace("", "")
            yield sources

    def retrieve_only(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve documents without LLM generation

        Args:
            query: User query
            top_k: Number of documents
            min_score: Score threshold

        Returns:
            List of retrieval results
        """
        k = top_k or self.top_k
        score = min_score or self.min_score

        processed_query = self.query_processor.preprocess(query)
        return self.retrieval_service.retrieve(
            query=processed_query,
            top_k=k,
            min_score=score,
        )

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG pipeline"""
        vector_stats = self.vector_store.get_stats()

        return {
            "vector_store": vector_stats,
            "embedding_model": str(self.embedding_service),
            "llm_model": str(self.llm),
            "top_k": self.top_k,
            "min_score": self.min_score,
        }

    def __repr__(self) -> str:
        return (
            f"RAGPipeline(llm={self.llm}, "
            f"top_k={self.top_k}, "
            f"min_score={self.min_score})"
        )
