"""
LangGraph Agent for Enhanced Chat
Implements a multi-step reasoning workflow with optional search integration

Here's a visual representation of the LangGraph workflow if _build_graph() is called:

          +----------------+
          |   AgentState  |
          +----------------+
                  |
                  | Entry Point
                  v
          +----------------+
          |   Analyzer     |
          +----------------+
                  |
                  | _should_search
                  v
+----------------+       +----------------+
|   Search       |       |   Responder     |
+----------------+       +----------------+
                  |       |
                  |       | _generate_response
                  |       v
                  +-------+
                            |
                            | END
                            v
          +----------------+
          |   END          |
          +----------------+

"""

from typing import TypedDict, Annotated, Sequence, AsyncIterator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
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

    def _prepare_messages_for_response(self, messages: Sequence[BaseMessage]) -> list[BaseMessage]:
        """
        Prepare messages for final response generation, handling Gemini's conversation requirements.

        Gemini requires conversations to end with a user message. When search tools are used,
        the message history contains AIMessages with tool_calls followed by ToolMessages.
        This method cleans the message history to be compatible with Gemini.

        Args:
            messages: Raw message history from state

        Returns:
            Cleaned message list compatible with Gemini API
        """
        # Separate user messages, search results, and final AI responses
        user_messages = []
        search_results = []
        ai_responses = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                user_messages.append(msg)
            elif isinstance(msg, ToolMessage):
                # Collect search results
                search_results.append(str(msg.content))
            elif isinstance(msg, AIMessage):
                # Only keep AI messages that are NOT tool calls (final responses)
                if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                    ai_responses.append(msg)

        # Build cleaned message list
        cleaned_messages = []

        # Add user messages (conversation history)
        cleaned_messages.extend(user_messages)

        # If we have search results, append them to the last user message
        if search_results and user_messages:
            # Enhance the last user message with search context
            last_user_msg = cleaned_messages[-1]
            original_content = last_user_msg.content
            context_text = "\n\n".join(search_results)
            enhanced_content = (
                f"{original_content}\n\n"
                f"[Search Results for Context]:\n{context_text}"
            )
            cleaned_messages[-1] = HumanMessage(content=enhanced_content)

        # Add any final AI responses (for multi-turn conversations)
        cleaned_messages.extend(ai_responses)

        # Fallback: ensure we have at least one message
        if not cleaned_messages and messages:
            # If somehow all messages were filtered, return the original human message
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    cleaned_messages.append(msg)
                    break

        return cleaned_messages

    def _generate_response(self, state: AgentState) -> dict:
        """
        Generate the final response based on conversation history and search results

        Args:
            state: Current agent state

        Returns:
            Updated state with final response
        """
        messages = state["messages"]

        # Clean messages for Gemini compatibility
        cleaned_messages = self._prepare_messages_for_response(messages)

        # Add system message for final response
        system_prompt = SystemMessage(
            content=(
                "You are a helpful, friendly, and knowledgeable AI assistant. "
                "Provide clear, accurate, and well-structured responses. "
                "If you used search results, synthesize the information naturally. "
                "Be concise but thorough in your answers."
            )
        )

        response = self.llm.invoke([system_prompt] + cleaned_messages)

        return {
            "messages": [response],
            "final_response": response.content,
        }

    async def astream(self, message: str) -> AsyncIterator[str]:
        """
        Stream chat response asynchronously with real-time token streaming

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

        # Check if we need to run analysis/search first
        if self.search_tools:
            # Run analyzer to check if search is needed
            analyzer_state = self._analyze_query(initial_state)

            # Properly merge messages (don't replace initial HumanMessage!)
            current_state = {
                "messages": initial_state["messages"] + analyzer_state.get("messages", []),
                "needs_search": analyzer_state.get("needs_search", False),
                "final_response": "",
            }

            # If search is needed, run search
            if self._should_search(current_state) == "search":
                # Execute search tools
                from langgraph.prebuilt import ToolNode
                tool_node = ToolNode(self.search_tools)
                search_result = await tool_node.ainvoke(current_state)

                # Merge search results
                current_state = {
                    "messages": current_state["messages"] + search_result["messages"],
                    "needs_search": False,
                    "final_response": "",
                }

            # Now stream the final response
            messages = current_state["messages"]
        else:
            # No search tools, use initial messages
            messages = initial_state["messages"]

        # Clean messages for Gemini compatibility
        cleaned_messages = self._prepare_messages_for_response(messages)

        # Add system message for final response
        system_prompt = SystemMessage(
            content=(
                "You are a helpful, friendly, and knowledgeable AI assistant. "
                "Provide clear, accurate, and well-structured responses. "
                "If you used search results, synthesize the information naturally. "
                "Be concise but thorough in your answers."
            )
        )

        # Stream the LLM response in real-time
        async for chunk in self.llm.astream([system_prompt] + cleaned_messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content

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
