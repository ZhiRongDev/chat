"""
LangGraph Agent for Enhanced Chat
Implements a multi-step reasoning workflow with optional search integration
"""

from typing import TypedDict, Annotated, Sequence, AsyncIterator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from app.service.llm.llm_factory import get_llm, LLMProvider
from app.service.llm.search_tools import SearchTools


class AgentState(TypedDict):
    """State definition for the agent graph"""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    needs_search: bool
    final_response: str


class ChatAgentGraph:
    """
    LangGraph-based chat agent with search and reasoning capabilities
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        use_search: bool = True,
        gemini_api_key: str | None = None,
        openai_api_key: str | None = None,
        anthropic_api_key: str | None = None,
    ):
        """
        Initialize the chat agent graph

        Args:
            provider: LLM provider to use
            model: Specific model name
            temperature: Generation temperature
            use_search: Whether to enable search tools
            gemini_api_key: User-provided Gemini API key
            openai_api_key: User-provided OpenAI API key
            anthropic_api_key: User-provided Anthropic API key
        """
        self.llm = get_llm(
            provider=provider,
            model=model,
            temperature=temperature,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
        )
        self.use_search = use_search and SearchTools.has_search_tools()
        self.search_tools = SearchTools.get_available_tools() if self.use_search else []

        # Bind tools to LLM if search is enabled
        if self.search_tools:
            self.llm_with_tools = self.llm.bind_tools(self.search_tools)
        else:
            self.llm_with_tools = self.llm

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyzer", self._analyze_query)
        workflow.add_node("responder", self._generate_response)

        if self.search_tools:
            workflow.add_node("search", ToolNode(self.search_tools))

        # Define edges
        workflow.set_entry_point("analyzer")

        if self.search_tools:
            # Conditional edge: search if needed, otherwise respond
            workflow.add_conditional_edges(
                "analyzer",
                self._should_search,
                {
                    "search": "search",
                    "respond": "responder",
                },
            )
            workflow.add_edge("search", "responder")
        else:
            # No search available, go directly to responder
            workflow.add_edge("analyzer", "responder")

        workflow.add_edge("responder", END)

        return workflow.compile()

    def _analyze_query(self, state: AgentState) -> dict:
        """
        Analyze the user query to determine if search is needed

        Args:
            state: Current agent state

        Returns:
            Updated state with needs_search flag
        """
        messages = state["messages"]

        # Add system message for analysis
        analysis_prompt = SystemMessage(
            content=(
                "You are a helpful AI assistant. Analyze the user's query and determine "
                "if you need to search for current information to answer accurately. "
                "If the query asks about recent events, current data, specific facts you "
                "might not know, or real-time information, you should use search tools. "
                "Otherwise, respond directly based on your knowledge."
            )
        )

        # For queries that likely need search, invoke tools
        if self.search_tools:
            response = self.llm_with_tools.invoke([analysis_prompt] + list(messages))
            needs_search = bool(response.tool_calls)

            return {
                "messages": [response],
                "needs_search": needs_search,
            }

        return {"needs_search": False}

    def _should_search(self, state: AgentState) -> str:
        """
        Determine if search should be performed

        Args:
            state: Current agent state

        Returns:
            Next node name ("search" or "respond")
        """
        messages = state["messages"]
        last_message = messages[-1]

        # Check if the last message has tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "search"

        return "respond"

    def _generate_response(self, state: AgentState) -> dict:
        """
        Generate the final response based on conversation history and search results

        Args:
            state: Current agent state

        Returns:
            Updated state with final response
        """
        messages = state["messages"]

        # Add system message for final response
        system_prompt = SystemMessage(
            content=(
                "You are a helpful, friendly, and knowledgeable AI assistant. "
                "Provide clear, accurate, and well-structured responses. "
                "If you used search results, synthesize the information naturally. "
                "Be concise but thorough in your answers."
            )
        )

        response = self.llm.invoke([system_prompt] + list(messages))

        return {
            "messages": [response],
            "final_response": response.content,
        }

    async def astream(self, message: str) -> AsyncIterator[str]:
        """
        Stream chat response asynchronously

        Args:
            message: User message

        Yields:
            Response chunks as strings
        """
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "needs_search": False,
            "final_response": "",
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Get the final AI message
        messages = final_state["messages"]
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                # Stream the content
                for char in msg.content:
                    yield char
                break

    async def astream_events(self, message: str) -> AsyncIterator[dict]:
        """
        Stream chat response with events for better control

        Args:
            message: User message

        Yields:
            Event dictionaries with type and data
        """
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "needs_search": False,
            "final_response": "",
        }

        # Stream graph execution
        async for event in self.graph.astream(initial_state, stream_mode="values"):
            # Get the latest message
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]

                if isinstance(last_message, AIMessage):
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        # Tool call event
                        yield {
                            "type": "tool_call",
                            "data": last_message.tool_calls,
                        }
                    elif last_message.content:
                        # Content event
                        yield {
                            "type": "content",
                            "data": last_message.content,
                        }

    def invoke(self, message: str) -> str:
        """
        Synchronous chat invocation (non-streaming)

        Args:
            message: User message

        Returns:
            Complete response string
        """
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "needs_search": False,
            "final_response": "",
        }

        final_state = self.graph.invoke(initial_state)
        return final_state.get("final_response", "")
