from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_serializer
from typing import Literal, Optional
from app.config import settings
from app.service.llm import ChatAgentGraph, LLMFactory, SearchTools
from app.service.chat_service import ChatService
from app.service.rag import RAGPipeline
from app.model.user_model import User
from app.model.chat_model import ChatHistory, ChatMessage
from app.auth import get_current_user
import asyncio


nonauth_router = APIRouter(prefix="/chat", tags=["chat"])
auth_router = APIRouter(prefix="/chat", tags=["chat"])


class ChatPayload(BaseModel):
    message: str
    provider: Literal["gemini", "openai", "anthropic"] | None = None
    model: str | None = None
    temperature: float = 0.7
    use_search: bool = True
    use_rag: bool = False  # Enable RAG mode
    top_k: int = 5  # Number of documents to retrieve for RAG
    min_score: float = 0.3  # Minimum relevance score for RAG


class ChatStatusResponse(BaseModel):
    """Response model for chat status endpoint"""

    available_providers: list[str]
    search_enabled: bool
    default_provider: str


@nonauth_router.get("/status", response_model=ChatStatusResponse)
async def get_chat_status():
    """
    Get available LLM providers and search status

    Returns information about which LLM providers are configured
    and whether search functionality is available.
    """
    return ChatStatusResponse(
        available_providers=LLMFactory.get_available_providers(),
        search_enabled=SearchTools.has_search_tools(),
        default_provider=settings.DEFAULT_LLM_PROVIDER,
    )


@nonauth_router.post("/")
async def chat_stream(payload: ChatPayload):
    """
    Enhanced chat endpoint with multi-LLM support, optional search, and RAG

    Features:
    - Multiple LLM providers (Gemini, OpenAI, Anthropic)
    - LangGraph-based reasoning workflow (when use_search=True, use_rag=False)
    - RAG mode with document retrieval (when use_rag=True)
    - Optional Google Search integration via Serper or Tavily
    - Streaming responses

    Args:
        payload: Chat payload with message and optional configuration

    Returns:
        StreamingResponse with text/plain content

    Raises:
        HTTPException: If message is missing or provider is not available
    """
    user_message = payload.message

    if not user_message:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    # Validate provider if specified
    if payload.provider:
        available_providers = LLMFactory.get_available_providers()
        if payload.provider not in available_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{payload.provider}' is not available. "
                f"Available providers: {', '.join(available_providers)}",
            )

    try:
        # Choose between RAG mode and standard agent mode
        if payload.use_rag:
            # RAG Pipeline mode
            rag_pipeline = RAGPipeline(
                llm_provider=payload.provider,
                llm_model=payload.model,
                llm_temperature=payload.temperature,
                top_k=payload.top_k,
                min_score=payload.min_score,
            )

            async def stream_rag_messages():
                """Stream RAG response"""
                try:
                    async for chunk in rag_pipeline.astream(user_message):
                        await asyncio.sleep(0)
                        yield chunk.encode("utf-8")

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
