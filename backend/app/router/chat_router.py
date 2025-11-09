from fastapi import APIRouter, HTTPException, status, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_serializer
from typing import Literal, Optional
from app.config import settings
from app.service.llm import ChatAgentGraph, LLMFactory, SearchTools
from app.service.chat_service import ChatService
from app.service.gemini_file_search_service import GeminiFileSearchService
from app.model.user_model import User
from app.model.chat_model import ChatHistory, ChatMessage
from app.model import engine
from app.auth import get_current_user, verify_access_token
from app.service.user_service import UserService
from sqlmodel import Session
import asyncio


nonauth_router = APIRouter(prefix="/chat", tags=["chat"])
auth_router = APIRouter(prefix="/chat", tags=["chat"])


class ChatPayload(BaseModel):
    message: str
    provider: Literal["gemini", "openai", "anthropic"] | None = None
    model: str | None = None
    temperature: float = 0.7
    use_search: bool = True
    use_rag: bool = False  # Enable RAG mode with Gemini File Search
    max_output_tokens: int = 2048  # Max tokens for RAG response
    # User-provided API keys (optional, overrides env vars)
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


class ChatStatusResponse(BaseModel):
    """Response model for chat status endpoint"""

    available_providers: list[str]
    supported_providers: list[str]
    search_enabled: bool
    default_provider: str


@nonauth_router.get("/status", response_model=ChatStatusResponse)
async def get_chat_status():
    """
    Get available LLM providers and search status

    Returns information about which LLM providers are configured
    and whether search functionality is available.

    Note: available_providers shows providers with API keys in environment.
    supported_providers shows all providers that can be used with user-provided keys.
    """
    return ChatStatusResponse(
        available_providers=LLMFactory.get_available_providers(),
        supported_providers=["gemini", "openai", "anthropic"],
        search_enabled=SearchTools.has_search_tools(),
        default_provider=settings.DEFAULT_LLM_PROVIDER,
    )


@nonauth_router.post("/")
async def chat_stream(
    payload: ChatPayload,
    authorization: Optional[str] = Header(None)
):
    """
    Chat endpoint with optional authentication

    Features:
    - Multiple LLM providers (Gemini, OpenAI, Anthropic)
    - LangGraph-based reasoning workflow
    - Gemini File Search RAG mode (when use_rag=True)
      - Uses personal document store if authenticated
      - Uses global document store if not authenticated
    - Optional Google Search integration via Serper or Tavily
    - Streaming responses

    Args:
        payload: Chat payload with message and optional configuration
        authorization: Optional Authorization header (for personal RAG store)

    Returns:
        StreamingResponse with text/plain content

    Raises:
        HTTPException: If message is missing or provider is not available
    """
    # Try to get user from Authorization header if present
    current_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.replace("Bearer ", "")
            token_data = verify_access_token(token)  # Returns dict with 'sub', 'reset', 'exp'
            username = token_data.get("sub") if isinstance(token_data, dict) else None
            if username:
                user_service = UserService()
                current_user = user_service.get_user_by_username(username)
        except Exception:
            # If token is invalid, just treat as non-authenticated
            pass

    return await _chat_stream_internal(payload, current_user=current_user)


async def _chat_stream_internal(payload: ChatPayload, current_user: Optional[User] = None):
    """
    Internal chat stream handler used by both authenticated and non-authenticated endpoints

    Args:
        payload: Chat payload with message and optional configuration
        current_user: Authenticated user (None if not authenticated)

    Returns:
        StreamingResponse with text/plain content

    Raises:
        HTTPException: If message is missing or provider is not available
    """
    user_message = payload.message

    if not user_message:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    # Auto-detect provider if not specified
    if not payload.provider:
        # Try to find an available provider based on API keys
        if payload.gemini_api_key or settings.GEMINI_API_KEY:
            payload.provider = "gemini"
        elif payload.openai_api_key or settings.OPENAI_API_KEY:
            payload.provider = "openai"
        elif payload.anthropic_api_key or settings.ANTHROPIC_API_KEY:
            payload.provider = "anthropic"
        else:
            raise HTTPException(
                status_code=400,
                detail="No API key configured. Please provide an API key for at least one provider "
                "(Gemini, OpenAI, or Anthropic) in settings or environment variables.",
            )

    # Validate provider if specified
    if payload.provider:
        # Check if provider is supported (regardless of env API keys)
        supported_providers = ["gemini", "openai", "anthropic"]
        if payload.provider not in supported_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{payload.provider}' is not supported. "
                f"Supported providers: {', '.join(supported_providers)}",
            )

        # Check if API key is available (either from env or user-provided)
        has_api_key = False
        if payload.provider == "gemini":
            has_api_key = bool(payload.gemini_api_key or settings.GEMINI_API_KEY)
        elif payload.provider == "openai":
            has_api_key = bool(payload.openai_api_key or settings.OPENAI_API_KEY)
        elif payload.provider == "anthropic":
            has_api_key = bool(payload.anthropic_api_key or settings.ANTHROPIC_API_KEY)

        if not has_api_key:
            raise HTTPException(
                status_code=400,
                detail=f"API key for provider '{payload.provider}' is not configured. "
                f"Please provide an API key or configure it in environment variables.",
            )

    try:
        # Choose between RAG mode and standard agent mode
        if payload.use_rag:
            # Gemini File Search RAG mode - only supports Gemini provider
            if payload.provider and payload.provider != "gemini":
                raise HTTPException(
                    status_code=400,
                    detail="RAG mode currently only supports Gemini provider. Please use provider='gemini' or omit provider parameter.",
                )

            # Force Gemini provider for RAG
            if not payload.provider:
                payload.provider = "gemini"

            # Check Gemini API key
            if not (payload.gemini_api_key or settings.GEMINI_API_KEY):
                raise HTTPException(
                    status_code=400,
                    detail="Gemini API key required for RAG mode. Please provide via gemini_api_key or configure in environment.",
                )

            gemini_service = GeminiFileSearchService()

            # Get File Search Store (user's store if authenticated, global store if not)
            with Session(engine) as session:
                if current_user:
                    # Use user's personal store
                    store = gemini_service.get_or_create_user_store(session, current_user.id)
                else:
                    # Use global store for non-authenticated users
                    store = gemini_service.get_or_create_global_store(session)

                # Check if store has any documents
                if store.document_count == 0:
                    if current_user:
                        detail_msg = "No documents found in your knowledge base. Please upload documents first using the Settings menu."
                    else:
                        detail_msg = "RAG mode is enabled but no documents are available in the shared knowledge base. Please log in to upload documents or disable RAG mode to continue."
                    raise HTTPException(
                        status_code=400,
                        detail=detail_msg,
                    )

                # Use the model from settings if not provided
                rag_model = payload.model or settings.GEMINI_FILE_SEARCH_MODEL

                async def stream_rag_messages():
                    """Stream RAG response from Gemini File Search"""
                    try:
                        # Query Gemini File Search (synchronous call, but we'll wrap it)
                        result = gemini_service.query_with_file_search(
                            query=user_message,
                            store_name=store.store_name,
                            model=rag_model,
                            temperature=payload.temperature,
                            max_output_tokens=payload.max_output_tokens
                        )

                        # Stream the content back
                        content = result['content']

                        # Stream character by character for smooth UX
                        for char in content:
                            await asyncio.sleep(0.01)  # Small delay for streaming effect
                            yield char.encode("utf-8")

                        # Optionally append citation info if available
                        if result.get('grounding_metadata'):
                            citations_msg = "\n\n[Sources: Retrieved from your documents]"
                            for char in citations_msg:
                                await asyncio.sleep(0.01)
                                yield char.encode("utf-8")

                    except Exception as e:
                        error_msg = f"Error during RAG generation: {str(e)}"
                        yield error_msg.encode("utf-8")

                return StreamingResponse(stream_rag_messages(), media_type="text/plain")

        else:
            # Standard agent mode with optional search
            agent = ChatAgentGraph(
                provider=payload.provider,
                model=payload.model,
                temperature=payload.temperature,
                use_search=payload.use_search,
                gemini_api_key=payload.gemini_api_key,
                openai_api_key=payload.openai_api_key,
                anthropic_api_key=payload.anthropic_api_key,
            )

            async def stream_messages():
                """Stream chat response using LangGraph agent"""
                try:
                    async for chunk in agent.astream(user_message):
                        await asyncio.sleep(0)
                        yield chunk.encode("utf-8")

                except Exception as e:
                    error_msg = f"Error during chat generation: {str(e)}"
                    yield error_msg.encode("utf-8")

            return StreamingResponse(stream_messages(), media_type="text/plain")

    except ValueError as e:
        # Handle LLM configuration errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# Chat History Management Endpoints (Authenticated)
# ============================================================================


class MessageData(BaseModel):
    """Message data for saving/receiving chat messages"""
    id: Optional[str] = None  # Frontend sends/receives str, backend uses int internally
    sender: str
    text: str


class SaveChatPayload(BaseModel):
    """Payload for saving/updating chat history"""
    chat_id: Optional[str] = None  # Frontend sends str, backend converts to int
    title: str
    messages: list[MessageData]


class ChatHistoryResponse(BaseModel):
    """Response model for chat history - returns str IDs to frontend"""
    id: str  # Snowflake ID as string for JavaScript safety
    title: str
    created_at: int
    updated_at: int
    message_count: int


class ChatDetailResponse(BaseModel):
    """Response model for chat detail with messages - returns str IDs to frontend"""
    id: str  # Snowflake ID as string for JavaScript safety
    title: str
    created_at: int
    updated_at: int
    messages: list[MessageData]


@auth_router.get("/history", response_model=list[ChatHistoryResponse])
async def get_chat_histories(
    current_user: User = Depends(get_current_user),
    limit: int = 100,
):
    """
    Get all chat histories for the authenticated user

    Args:
        current_user: Authenticated user from JWT token
        limit: Maximum number of chats to return (default: 100)

    Returns:
        List of chat histories with message counts (IDs as strings)
    """
    chat_service = ChatService()
    chats = chat_service.get_all_chat_histories(user_id=current_user.id, limit=limit)

    # Convert int IDs from database to str for frontend
    return [
        ChatHistoryResponse(
            id=chat["id"],  # chat["id"] is already str from service
            title=chat["title"],
            created_at=chat["created_at"],
            updated_at=chat["updated_at"],
            message_count=chat["message_count"],
        )
        for chat in chats
    ]


@auth_router.get("/history/{chat_id}", response_model=ChatDetailResponse)
async def get_chat_detail(
    chat_id: str,  # Receive as str from frontend
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific chat history with all messages

    Args:
        chat_id: Chat history ID (Snowflake ID as string from frontend)
        current_user: Authenticated user from JWT token

    Returns:
        Chat history with all messages (IDs as strings)

    Raises:
        HTTPException: If chat not found or doesn't belong to user
    """
    # Convert string ID to int for database query
    try:
        chat_id_int = int(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chat_id format",
        )

    chat_service = ChatService()
    chat = chat_service.get_chat_history_by_id(chat_id_int, user_id=current_user.id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history not found",
        )

    messages = chat_service.get_messages_by_chat_id(chat_id_int)

    # Convert int IDs to str for frontend
    return ChatDetailResponse(
        id=str(chat.id),
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[
            MessageData(id=str(msg.id), sender=msg.sender, text=msg.text)
            for msg in messages
        ],
    )


@auth_router.post("/history", response_model=ChatDetailResponse)
async def save_chat_history(
    payload: SaveChatPayload,  # Receives str IDs from frontend
    current_user: User = Depends(get_current_user),
):
    """
    Save or update a chat history with messages

    Args:
        payload: Chat data with str IDs from frontend
        current_user: Authenticated user from JWT token

    Returns:
        Saved chat history with messages (IDs as strings)

    Raises:
        HTTPException: If chat_id provided but not found or doesn't belong to user
    """
    chat_service = ChatService()

    try:
        # Convert string chat_id to int for database if provided
        chat_id_int = None
        if payload.chat_id:
            try:
                chat_id_int = int(payload.chat_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid chat_id format",
                )

        # Convert MessageData to dict for service (message IDs are ignored when saving)
        messages_data = [
            {"sender": msg.sender, "text": msg.text}
            for msg in payload.messages
        ]

        chat = chat_service.save_chat_with_messages(
            chat_id=chat_id_int,
            user_id=current_user.id,
            title=payload.title,
            messages=messages_data,
        )

        # Get messages for response
        messages = chat_service.get_messages_by_chat_id(chat.id)

        # Convert int IDs to str for frontend
        return ChatDetailResponse(
            id=str(chat.id),
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            messages=[
                MessageData(id=str(msg.id), sender=msg.sender, text=msg.text)
                for msg in messages
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save chat: {str(e)}",
        )


@auth_router.delete("/history/{chat_id}")
async def delete_chat_history(
    chat_id: str,  # Receive as str from frontend
    current_user: User = Depends(get_current_user),
):
    """
    Delete a chat history and all its messages

    Args:
        chat_id: Chat history ID (Snowflake ID as string from frontend)
        current_user: Authenticated user from JWT token

    Returns:
        Success message

    Raises:
        HTTPException: If chat not found or doesn't belong to user
    """
    # Convert string ID to int for database query
    try:
        chat_id_int = int(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chat_id format",
        )

    chat_service = ChatService()
    deleted = chat_service.delete_chat_history(chat_id_int, user_id=current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history not found",
        )

    return {"detail": "Chat history deleted successfully"}
