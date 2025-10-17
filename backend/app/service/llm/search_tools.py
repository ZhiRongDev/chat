"""
Search Tools Integration
Supports: Serper (Google Search), Tavily Search
"""

from typing import Any
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from app.config import settings


class SearchTools:
    """Factory class for creating search tool instances"""

    @staticmethod
    def create_serper_search() -> Tool | None:
        """
        Create a Google Search tool using Serper API

        Returns:
            Tool instance or None if API key is not configured
        """
        if not settings.SERPER_API_KEY:
            return None

        search = GoogleSerperAPIWrapper(
            serper_api_key=settings.SERPER_API_KEY,
            k=5,  # Number of results
        )

        return Tool(
            name="google_search",
            description=(
                "Useful for searching current information on the internet. "
                "Use this when you need up-to-date information, facts, news, or "
                "when the user's question requires recent data. "
                "Input should be a search query string."
            ),
            func=search.run,
        )

    @staticmethod
    def create_tavily_search() -> Tool | None:
        """
        Create a Tavily search tool

        Returns:
            Tool instance or None if API key is not configured
        """
        if not settings.TAVILY_API_KEY:
            return None

        try:
            from langchain_community.tools.tavily_search import TavilySearchResults

            tavily_search = TavilySearchResults(
                api_key=settings.TAVILY_API_KEY,
                max_results=5,
            )

            return Tool(
                name="tavily_search",
                description=(
                    "A search engine optimized for comprehensive, accurate, and trusted results. "
                    "Useful for answering questions about current events, research topics, "
                    "and general knowledge queries. Input should be a search query string."
                ),
                func=tavily_search.invoke,
            )
        except ImportError:
            return None

    @staticmethod
    def get_available_tools() -> list[Tool]:
        """
        Get all available search tools based on configured API keys

        Returns:
            List of available search Tool instances
        """
        tools = []

        serper_tool = SearchTools.create_serper_search()
        if serper_tool:
            tools.append(serper_tool)

        tavily_tool = SearchTools.create_tavily_search()
        if tavily_tool:
            tools.append(tavily_tool)

        return tools

    @staticmethod
    def has_search_tools() -> bool:
        """
        Check if any search tools are available

        Returns:
            True if at least one search tool is configured
        """
        return bool(settings.SERPER_API_KEY or settings.TAVILY_API_KEY)
