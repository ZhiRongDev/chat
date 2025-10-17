#!/usr/bin/env python3
"""
Example script demonstrating the enhanced chat system with LangGraph

This script shows how to use the new multi-provider chat system with
search capabilities.

Prerequisites:
1. Install dependencies: pip install -r requirements.txt
2. Configure .env with at least one LLM API key
3. Optional: Add search API keys for enhanced results

Usage:
    python examples/chat_example.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.service.llm import ChatAgentGraph, LLMFactory, SearchTools
from app.config import settings


async def example_basic_chat():
    """Example 1: Basic chat without search"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Chat (No Search)")
    print("=" * 60)

    agent = ChatAgentGraph(use_search=False)

    question = "What is LangGraph?"
    print(f"\nQuestion: {question}")
    print("\nResponse:", end=" ", flush=True)

    async for chunk in agent.astream(question):
        print(chunk, end="", flush=True)

    print("\n")


async def example_search_chat():
    """Example 2: Chat with search enabled"""
    print("\n" + "=" * 60)
    print("Example 2: Chat with Search")
    print("=" * 60)

    if not SearchTools.has_search_tools():
        print("\n⚠️  Search is not configured. Add SERPER_API_KEY or TAVILY_API_KEY to .env")
        return

    agent = ChatAgentGraph(use_search=True)

    question = "What are the latest developments in artificial intelligence?"
    print(f"\nQuestion: {question}")
    print("\nResponse:", end=" ", flush=True)

    async for chunk in agent.astream(question):
        print(chunk, end="", flush=True)

    print("\n")


async def example_multi_provider():
    """Example 3: Compare responses from different providers"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Provider Comparison")
    print("=" * 60)

    available_providers = LLMFactory.get_available_providers()
    print(f"\nAvailable providers: {', '.join(available_providers)}")

    question = "Explain quantum computing in one sentence."

    for provider in available_providers:
        print(f"\n--- {provider.upper()} ---")
        print(f"Question: {question}")
        print("Response:", end=" ", flush=True)

        agent = ChatAgentGraph(provider=provider, use_search=False)

        async for chunk in agent.astream(question):
            print(chunk, end="", flush=True)

        print()


async def example_temperature_comparison():
    """Example 4: Compare different temperature settings"""
    print("\n" + "=" * 60)
    print("Example 4: Temperature Comparison")
    print("=" * 60)

    question = "Write a creative opening line for a sci-fi novel."

    temperatures = [0.1, 0.7, 1.0]

    for temp in temperatures:
        print(f"\n--- Temperature: {temp} ---")
        print(f"Question: {question}")
        print("Response:", end=" ", flush=True)

        agent = ChatAgentGraph(temperature=temp, use_search=False)

        async for chunk in agent.astream(question):
            print(chunk, end="", flush=True)

        print()


async def example_streaming_vs_sync():
    """Example 5: Streaming vs synchronous responses"""
    print("\n" + "=" * 60)
    print("Example 5: Streaming vs Synchronous")
    print("=" * 60)

    agent = ChatAgentGraph(use_search=False)
    question = "What is Python?"

    # Synchronous (complete response)
    print("\n--- Synchronous Response ---")
    print(f"Question: {question}")
    response = agent.invoke(question)
    print(f"Response: {response}\n")

    # Streaming (token by token)
    print("--- Streaming Response ---")
    print(f"Question: {question}")
    print("Response:", end=" ", flush=True)

    async for chunk in agent.astream(question):
        print(chunk, end="", flush=True)

    print("\n")


def print_system_status():
    """Print current system configuration"""
    print("\n" + "=" * 60)
    print("System Status")
    print("=" * 60)

    print(f"\nDefault LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")

    providers = LLMFactory.get_available_providers()
    print(f"Available LLM Providers: {', '.join(providers) if providers else 'None'}")

    search_enabled = SearchTools.has_search_tools()
    print(f"Search Enabled: {search_enabled}")

    if search_enabled:
        print("\nConfigured Search Tools:")
        if settings.SERPER_API_KEY:
            print("  ✓ Serper (Google Search)")
        if settings.TAVILY_API_KEY:
            print("  ✓ Tavily Search")

    print()


async def interactive_chat():
    """Example 6: Interactive chat session"""
    print("\n" + "=" * 60)
    print("Interactive Chat Session")
    print("=" * 60)
    print("\nType your messages below. Commands:")
    print("  /quit - Exit")
    print("  /search on|off - Toggle search")
    print("  /provider <name> - Switch provider")
    print("  /providers - List available providers")
    print()

    # Default settings
    use_search = SearchTools.has_search_tools()
    provider = None  # Use default

    agent = ChatAgentGraph(provider=provider, use_search=use_search)

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                if user_input == "/quit":
                    print("Goodbye!")
                    break

                elif user_input == "/search on":
                    if SearchTools.has_search_tools():
                        use_search = True
                        agent = ChatAgentGraph(provider=provider, use_search=use_search)
                        print("✓ Search enabled")
                    else:
                        print("⚠️  Search not available. Configure SERPER_API_KEY or TAVILY_API_KEY")
                    continue

                elif user_input == "/search off":
                    use_search = False
                    agent = ChatAgentGraph(provider=provider, use_search=use_search)
                    print("✓ Search disabled")
                    continue

                elif user_input.startswith("/provider "):
                    new_provider = user_input.split(" ", 1)[1].strip()
                    available = LLMFactory.get_available_providers()
                    if new_provider in available:
                        provider = new_provider
                        agent = ChatAgentGraph(provider=provider, use_search=use_search)
                        print(f"✓ Switched to {new_provider}")
                    else:
                        print(f"⚠️  Provider not available. Available: {', '.join(available)}")
                    continue

                elif user_input == "/providers":
                    providers = LLMFactory.get_available_providers()
                    print(f"Available providers: {', '.join(providers)}")
                    print(f"Current: {provider or settings.DEFAULT_LLM_PROVIDER}")
                    continue

                else:
                    print("Unknown command. Available: /quit, /search, /provider, /providers")
                    continue

            # Regular chat message
            print("Assistant:", end=" ", flush=True)

            async for chunk in agent.astream(user_input):
                print(chunk, end="", flush=True)

            print("\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}\n")


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("LangGraph Chat System Examples")
    print("=" * 60)

    # Show system status
    print_system_status()

    # Check if any provider is available
    if not LLMFactory.get_available_providers():
        print("\n⚠️  ERROR: No LLM providers configured!")
        print("Please add at least one API key to your .env file:")
        print("  - GEMINI_API_KEY")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        return

    # Run examples
    print("\nChoose an example to run:")
    print("1. Basic chat (no search)")
    print("2. Chat with search")
    print("3. Multi-provider comparison")
    print("4. Temperature comparison")
    print("5. Streaming vs synchronous")
    print("6. Interactive chat session")
    print("0. Run all non-interactive examples")

    try:
        choice = input("\nEnter choice (0-6): ").strip()

        if choice == "1":
            await example_basic_chat()
        elif choice == "2":
            await example_search_chat()
        elif choice == "3":
            await example_multi_provider()
        elif choice == "4":
            await example_temperature_comparison()
        elif choice == "5":
            await example_streaming_vs_sync()
        elif choice == "6":
            await interactive_chat()
        elif choice == "0":
            await example_basic_chat()
            await example_search_chat()
            await example_multi_provider()
            await example_temperature_comparison()
            await example_streaming_vs_sync()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\n\nExiting...")


if __name__ == "__main__":
    asyncio.run(main())
