from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal, Optional
from app.config import settings
from app.service.llm import ChatAgentGraph, LLMFactory, SearchTools
from app.service.chat_service import ChatService
from app.service.gemini_file_search_service import GeminiFileSearchService
from app.model.user_model import User
from app.model.document_model import Document
import app.model
from app.auth import get_current_user
from app.middleware import check_chat_rate_limit
from sqlmodel import Session, select
import asyncio
import logging


nonauth_router = APIRouter(prefix="/chat", tags=["chat"])
auth_router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])

# Configure logger
logger = logging.getLogger(__name__)


class ChatPayload(BaseModel):
    message: str
    provider: Literal["gemini", "openai", "anthropic"] | None = None
    model: str | None = None
    temperature: float = 0.7
    use_search: bool = True
    use_rag: bool = False  # Enable RAG mode with Gemini File Search
    max_output_tokens: int = 2048  # Max tokens for RAG response


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


@auth_router.post("/")
async def chat_stream(
    payload: ChatPayload,
    current_user: User = Depends(get_current_user),
):
    """
    Chat endpoint (requires authentication and rate limiting)

    Features:
    - Multiple LLM providers (Gemini, OpenAI, Anthropic)
    - LangGraph-based reasoning workflow
    - Gemini File Search RAG mode (when use_rag=True)
      - Each user has their own personal document store (one store per user_id)
    - Optional Google Search integration via Serper or Tavily
    - Streaming responses
    - Rate limiting: 20 messages per 30 minutes per user

    Args:
        payload: Chat payload with message and optional configuration
        current_user: Authenticated user (required)

    Returns:
        StreamingResponse with text/plain content

    Raises:
        HTTPException: If message is missing, provider is not available, or rate limit exceeded
    """
    # Check rate limit before processing
    check_chat_rate_limit(current_user.id)

    return await _chat_stream_internal(payload, current_user=current_user)


def _extract_document_references(grounding_metadata, session: Session) -> list[dict]:
    """
    Extract document references from Gemini grounding metadata

    Args:
        grounding_metadata: Grounding metadata from Gemini response
        session: Database session

    Returns:
        List of document info dicts with filename, file_type, etc.
    """
    if not grounding_metadata:
        return []

    document_refs = []
    seen_file_ids = set()

    try:
        # Extract grounding chunks which contain document references
        if hasattr(grounding_metadata, "grounding_chunks"):
            for chunk in grounding_metadata.grounding_chunks:
                # Check if this is a retrieved context (from file search)
                if hasattr(chunk, "retrieved_context"):
                    retrieved = chunk.retrieved_context

                    # Extract URI which contains the file ID
                    if hasattr(retrieved, "uri"):
                        uri = retrieved.uri
                        # URI format: "fileSearchStores/{store_id}/documents/{file_id}"
                        # Extract the file_id from URI
                        if "/documents/" in uri:
                            file_id_part = uri.split("/documents/")[-1]

                            # Skip if we've already processed this file
                            if file_id_part in seen_file_ids:
                                continue
                            seen_file_ids.add(file_id_part)

                            # Query database for document details using gemini_file_id
                            # The gemini_file_id in DB should match the full document path
                            stmt = select(Document).where(
                                Document.gemini_file_id.contains(file_id_part)
                            )
                            doc = session.exec(stmt).first()

                            if doc:
                                document_refs.append(
                                    {
                                        "filename": doc.filename,
                                        "file_type": doc.file_type,
                                        "file_size": doc.file_size,
                                    }
                                )
                            else:
                                # Fallback: Use title from retrieved context if available
                                title = (
                                    retrieved.title
                                    if hasattr(retrieved, "title")
                                    else "Unknown Document"
                                )
                                document_refs.append(
                                    {
                                        "filename": title,
                                        "file_type": "unknown",
                                        "file_size": 0,
                                    }
                                )
    except Exception as e:
        logger.error(f"Error extracting document references: {e}")

    return document_refs


async def _chat_stream_internal(payload: ChatPayload, current_user: User):
    """
    Internal chat stream handler

    Args:
        payload: Chat payload with message and optional configuration
        current_user: Authenticated user (required)

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
        # Try to find an available provider based on server-configured API keys
        if settings.GEMINI_API_KEY:
            payload.provider = "gemini"
        elif settings.OPENAI_API_KEY:
            payload.provider = "openai"
        elif settings.ANTHROPIC_API_KEY:
            payload.provider = "anthropic"
        else:
            raise HTTPException(
                status_code=400,
                detail="No LLM API key configured on the server. Please contact your administrator.",
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

        # Check if API key is available on server
        has_api_key = False
        if payload.provider == "gemini":
            has_api_key = bool(settings.GEMINI_API_KEY)
        elif payload.provider == "openai":
            has_api_key = bool(settings.OPENAI_API_KEY)
        elif payload.provider == "anthropic":
            has_api_key = bool(settings.ANTHROPIC_API_KEY)

        if not has_api_key:
            raise HTTPException(
                status_code=400,
                detail=f"API key for provider '{payload.provider}' is not configured on the server. "
                f"Please contact your administrator.",
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
            if not settings.GEMINI_API_KEY:
                raise HTTPException(
                    status_code=400,
                    detail="Gemini API key required for RAG mode. Please contact your administrator.",
                )

            # Initialize Gemini service with server-configured API key
            gemini_service = GeminiFileSearchService()

            # Get user's personal File Search Store
            with Session(app.model.engine) as session:
                store = gemini_service.get_or_create_user_store(
                    session, current_user.id
                )

                print(f"store: {store}")

                # Check if store has any documents by querying the database directly
                # (don't rely on cached store.document_count which may be stale)
                documents = gemini_service.list_documents(
                    db=session, user_id=current_user.id, store_id=store.id, limit=1
                )

                print(f"documents: {documents}")

                if not documents:
                    raise HTTPException(
                        status_code=400,
                        detail="No documents found in your knowledge base. Please upload documents first using the Settings menu.",
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
                            max_output_tokens=payload.max_output_tokens,
                        )

                        # Stream the content back
                        content = result["content"]

                        # Stream character by character for smooth UX
                        for char in content:
                            await asyncio.sleep(
                                0.01
                            )  # Small delay for streaming effect
                            yield char.encode("utf-8")

                        # Extract and format document references if available
                        if result.get("grounding_metadata"):
                            # Extract document references from grounding metadata
                            document_refs = _extract_document_references(
                                result["grounding_metadata"], session
                            )

                            if document_refs:
                                # Format document references
                                citations_msg = (
                                    "\n\n---\n\n**📚 Referenced Documents:**\n\n"
                                )
                                for idx, doc_ref in enumerate(document_refs, 1):
                                    filename = doc_ref["filename"]
                                    file_type = doc_ref["file_type"].upper()

                                    # Format file size
                                    file_size = doc_ref["file_size"]
                                    if file_size < 1024:
                                        size_str = f"{file_size} B"
                                    elif file_size < 1024 * 1024:
                                        size_str = f"{file_size / 1024:.1f} KB"
                                    else:
                                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                                    citations_msg += f"{idx}. **{filename}** ({file_type}, {size_str})\n"

                                # Stream the formatted citations
                                for char in citations_msg:
                                    await asyncio.sleep(
                                        0.005
                                    )  # Faster streaming for citations
                                    yield char.encode("utf-8")
                            else:
                                # Generic fallback if we can't extract specific documents
                                citations_msg = "\n\n---\n\n*📄 This response was generated using information from your uploaded documents.*"
                                for char in citations_msg:
                                    await asyncio.sleep(0.005)
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
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
            {"sender": msg.sender, "text": msg.text} for msg in payload.messages
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
