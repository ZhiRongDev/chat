"""
Prompt Builder Service for RAG
Constructs prompts with retrieved context for LLM input
"""

from typing import List, Optional, Dict, Any
from app.service.rag.retrieval_service import RetrievalResult


class PromptBuilder:
    """
    Service for building prompts with retrieved context
    Formats context documents and user queries for LLM input
    """

    DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant with access to a knowledge base. Use the provided context to answer the user's question accurately and comprehensively.

Guidelines:
- Answer based primarily on the provided context
- If the context doesn't contain relevant information, say so clearly
- Cite specific parts of the context when possible
- Be concise but thorough
- If you're uncertain, acknowledge it"""

    DEFAULT_CONTEXT_TEMPLATE = """Context from {source}:
{content}"""

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        context_template: Optional[str] = None,
        max_context_length: int = 4000,
        include_metadata: bool = True,
    ):
        """
        Initialize prompt builder

        Args:
            system_prompt: System prompt template
            context_template: Template for formatting context
            max_context_length: Maximum characters for context
            include_metadata: Whether to include metadata in context
        """
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.context_template = context_template or self.DEFAULT_CONTEXT_TEMPLATE
        self.max_context_length = max_context_length
        self.include_metadata = include_metadata

    def build_context(self, results: List[RetrievalResult]) -> str:
        """
        Build context string from retrieval results

        Args:
            results: List of retrieval results

        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant context found."

        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            # Format source information
            source = result.document_title or f"Document {result.document_id}"
            if result.chunk_index is not None:
                source += f" (Chunk {result.chunk_index + 1})"

            # Format context with metadata if enabled
            if self.include_metadata and result.metadata:
                metadata_str = self._format_metadata(result.metadata)
                content = f"{result.content}\n{metadata_str}"
            else:
                content = result.content

            # Format using template
            formatted = self.context_template.format(
                source=source,
                content=content,
            )

            # Check length limit
            if current_length + len(formatted) > self.max_context_length:
                break

            context_parts.append(f"[{i}] {formatted}")
            current_length += len(formatted)

        return "\n\n".join(context_parts)

    def build_prompt(
        self,
        query: str,
        results: List[RetrievalResult],
        include_system_prompt: bool = True,
    ) -> Dict[str, str]:
        """
        Build complete prompt with system message, context, and query

        Args:
            query: User query
            results: Retrieval results
            include_system_prompt: Whether to include system prompt

        Returns:
            Dictionary with 'system', 'context', and 'query' keys
        """
        context = self.build_context(results)

        prompt_parts = {
            "query": query,
            "context": context,
        }

        if include_system_prompt:
            prompt_parts["system"] = self.system_prompt

        return prompt_parts

    def build_prompt_string(
        self,
        query: str,
        results: List[RetrievalResult],
        format_style: str = "chat",
    ) -> str:
        """
        Build a single formatted prompt string

        Args:
            query: User query
            results: Retrieval results
            format_style: 'chat' or 'completion' style

        Returns:
            Formatted prompt string
        """
        context = self.build_context(results)

        if format_style == "chat":
            # Format for chat models
            return f"""{self.system_prompt}

---
CONTEXT:
{context}

---
USER QUERY:
{query}

---
ASSISTANT RESPONSE:"""

        else:  # completion style
            return f"""Context Information:
{context}

Question: {query}

Answer:"""

    def build_messages(
        self,
        query: str,
        results: List[RetrievalResult],
    ) -> List[Dict[str, str]]:
        """
        Build messages array for chat completion APIs

        Args:
            query: User query
            results: Retrieval results

        Returns:
            List of message dictionaries
        """
        context = self.build_context(results)

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": f"""I have a question. Here's some relevant context:

{context}

My question: {query}

Please answer based on the provided context.""",
            },
        ]

        return messages

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as readable string"""
        if not metadata:
            return ""

        # Filter out None values and format
        filtered = {k: v for k, v in metadata.items() if v is not None}

        if not filtered:
            return ""

        items = [f"{k}: {v}" for k, v in filtered.items()]
        return f"[Metadata: {', '.join(items)}]"

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimate of token count (4 chars ≈ 1 token)

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def truncate_context(
        self,
        results: List[RetrievalResult],
        max_tokens: int = 2000,
    ) -> List[RetrievalResult]:
        """
        Truncate results to fit within token limit

        Args:
            results: Retrieval results
            max_tokens: Maximum tokens for context

        Returns:
            Truncated list of results
        """
        truncated = []
        token_count = 0

        for result in results:
            result_tokens = self.estimate_tokens(result.content)

            if token_count + result_tokens > max_tokens:
                break

            truncated.append(result)
            token_count += result_tokens

        return truncated

    def add_citations(
        self,
        response: str,
        results: List[RetrievalResult],
    ) -> str:
        """
        Add citations/sources to response

        Args:
            response: LLM response text
            results: Retrieval results used

        Returns:
            Response with citations appended
        """
        if not results:
            return response

        citations = ["\n\nSources:"]
        for i, result in enumerate(results, 1):
            source = result.document_title or f"Document {result.document_id}"
            if result.chunk_index is not None:
                source += f" (Chunk {result.chunk_index + 1})"
            citations.append(f"[{i}] {source} (relevance: {result.score:.2f})")

        return response + "\n".join(citations)

    def __repr__(self) -> str:
        return f"PromptBuilder(max_context_length={self.max_context_length})"
