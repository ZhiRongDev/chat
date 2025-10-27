"""
LLM Factory for Multi-Provider Support
Supports: Google Gemini, OpenAI, Anthropic Claude
"""

from typing import Literal
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.config import settings

LLMProvider = Literal["gemini", "openai", "anthropic"]


class LLMFactory:
    """Factory class for creating LLM instances"""

    @staticmethod
    def create_llm(
        provider: LLMProvider | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        streaming: bool = True,
    ) -> BaseChatModel:
        """
        Create an LLM instance based on the provider

        Args:
            provider: LLM provider (gemini, openai, anthropic). Defaults to DEFAULT_LLM_PROVIDER
            model: Specific model name. If None, uses provider's default
            temperature: Temperature for generation (0.0 to 1.0)
            streaming: Enable streaming responses

        Returns:
            BaseChatModel instance

        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        provider = provider or settings.DEFAULT_LLM_PROVIDER

        if provider == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not configured")
            return ChatGoogleGenerativeAI(
                model=model or "gemini-2.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=temperature,
                streaming=streaming,
            )

        elif provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not configured")
            return ChatOpenAI(
                model=model or "gpt-4o-mini",
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=temperature,
                streaming=streaming,
            )

        elif provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY is not configured")
            return ChatAnthropic(
                model=model or "claude-3-5-sonnet-20241022",
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=temperature,
                streaming=streaming,
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: gemini, openai, anthropic"
            )

    @staticmethod
    def get_available_providers() -> list[str]:
        """
        Get list of available providers based on configured API keys

        Returns:
            List of available provider names
        """
        providers = []
        if settings.GEMINI_API_KEY:
            providers.append("gemini")
        if settings.OPENAI_API_KEY:
            providers.append("openai")
        if settings.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        return providers


def get_llm(
    provider: LLMProvider | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    streaming: bool = True,
) -> BaseChatModel:
    """
    Convenience function to create an LLM instance

    Args:
        provider: LLM provider (gemini, openai, anthropic)
        model: Specific model name
        temperature: Temperature for generation
        streaming: Enable streaming responses

    Returns:
        BaseChatModel instance
    """
    return LLMFactory.create_llm(provider, model, temperature, streaming)
