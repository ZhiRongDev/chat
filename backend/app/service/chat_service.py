from app.model.chat_model import ChatHistory, ChatMessage
from app.model import engine
from sqlmodel import Session, select, desc
from typing import Optional
from app.utils import get_timestamp


class ChatService:
    """Service for managing chat history and messages"""

    @staticmethod
    def create_chat_history(
        user_id: Optional[int], title: str
    ) -> ChatHistory:
        """Create a new chat history record"""
        with Session(engine) as session:
            chat_history = ChatHistory(
                user_id=user_id,
                title=title,
                created_at=get_timestamp(),
                updated_at=get_timestamp(),
            )
            session.add(chat_history)
            session.commit()
            session.refresh(chat_history)
        return chat_history

    @staticmethod
    def get_chat_history_by_id(
        chat_id: int, user_id: Optional[int] = None
    ) -> Optional[ChatHistory]:
        """Get a chat history by ID, optionally filtered by user_id"""
        with Session(engine) as session:
            statement = select(ChatHistory).where(ChatHistory.id == chat_id)
            if user_id is not None:
                statement = statement.where(ChatHistory.user_id == user_id)
            result = session.exec(statement).first()
        return result

    @staticmethod
    def get_all_chat_histories(
        user_id: Optional[int] = None, limit: int = 100
    ) -> list[dict]:
        """Get all chat histories with message counts, optionally filtered by user_id, sorted by created_at (newest first)"""
        with Session(engine) as session:
            statement = select(ChatHistory).order_by(desc(ChatHistory.created_at)).limit(limit)
            if user_id is not None:
                statement = statement.where(ChatHistory.user_id == user_id)
            results = session.exec(statement).all()

            # Convert to dict with message count calculated within session
            # Note: IDs are returned as strings for JavaScript safety (Snowflake IDs exceed JS Number.MAX_SAFE_INTEGER)
            chat_list = []
            for chat in results:
                # Count messages for this chat
                message_count = session.exec(
                    select(ChatMessage).where(ChatMessage.chat_history_id == chat.id)
                ).all()

                chat_list.append({
                    "id": str(chat.id),  # Convert to string for frontend
                    "user_id": str(chat.user_id) if chat.user_id else None,
                    "title": chat.title,
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at,
                    "message_count": len(message_count),
                })
        return chat_list

    @staticmethod
    def update_chat_history(
        chat_id: int, title: Optional[str] = None, user_id: Optional[int] = None
    ) -> Optional[ChatHistory]:
        """Update a chat history record"""
        with Session(engine) as session:
            statement = select(ChatHistory).where(ChatHistory.id == chat_id)
            if user_id is not None:
                statement = statement.where(ChatHistory.user_id == user_id)

            chat_history = session.exec(statement).first()
            if not chat_history:
                return None

            if title is not None:
                chat_history.title = title
            chat_history.updated_at = get_timestamp()

            session.add(chat_history)
            session.commit()
            session.refresh(chat_history)
        return chat_history

    @staticmethod
    def delete_chat_history(chat_id: int, user_id: Optional[int] = None) -> bool:
        """Delete a chat history and all its messages (cascade)"""
        with Session(engine) as session:
            statement = select(ChatHistory).where(ChatHistory.id == chat_id)
            if user_id is not None:
                statement = statement.where(ChatHistory.user_id == user_id)

            chat_history = session.exec(statement).first()
            if not chat_history:
                return False

            session.delete(chat_history)
            session.commit()
        return True

    @staticmethod
    def add_message(
        chat_id: int, sender: str, text: str, message_order: int
    ) -> ChatMessage:
        """Add a message to a chat history"""
        with Session(engine) as session:
            message = ChatMessage(
                chat_history_id=chat_id,
                sender=sender,
                text=text,
                message_order=message_order,
            )
            session.add(message)
            session.commit()
            session.refresh(message)
        return message

    @staticmethod
    def get_messages_by_chat_id(chat_id: int) -> list[ChatMessage]:
        """Get all messages for a chat history, ordered by message_order"""
        with Session(engine) as session:
            statement = (
                select(ChatMessage)
                .where(ChatMessage.chat_history_id == chat_id)
                .order_by(ChatMessage.message_order)
            )
            results = session.exec(statement).all()
        return list(results)

    @staticmethod
    def save_chat_with_messages(
        chat_id: Optional[int],
        user_id: Optional[int],
        title: str,
        messages: list[dict],
    ) -> ChatHistory:
        """
        Save or update a complete chat history with messages.
        If chat_id is None, creates a new chat. Otherwise updates existing.

        Args:
            chat_id: Existing chat ID or None for new chat
            user_id: User ID or None for anonymous
            title: Chat title
            messages: List of dicts with 'sender', 'text', 'id' keys

        Returns:
            ChatHistory object with messages
        """
        with Session(engine) as session:
            if chat_id:
                # Update existing chat
                statement = select(ChatHistory).where(ChatHistory.id == chat_id)
                if user_id is not None:
                    statement = statement.where(ChatHistory.user_id == user_id)

                chat_history = session.exec(statement).first()
                if not chat_history:
                    raise ValueError(f"Chat history with id {chat_id} not found")

                # Update title and timestamp
                chat_history.title = title
                chat_history.updated_at = get_timestamp()

                # Delete old messages
                old_messages = session.exec(
                    select(ChatMessage).where(ChatMessage.chat_history_id == chat_id)
                ).all()
                for msg in old_messages:
                    session.delete(msg)
            else:
                # Create new chat
                chat_history = ChatHistory(
                    user_id=user_id,
                    title=title,
                    created_at=get_timestamp(),
                    updated_at=get_timestamp(),
                )
                session.add(chat_history)
                session.flush()  # Get the ID without committing

            # Add all messages
            for idx, msg_data in enumerate(messages):
                message = ChatMessage(
                    chat_history_id=chat_history.id,
                    sender=msg_data["sender"],
                    text=msg_data["text"],
                    message_order=idx,
                )
                session.add(message)

            session.commit()
            session.refresh(chat_history)

            # Load messages relationship
            statement = select(ChatHistory).where(ChatHistory.id == chat_history.id)
            chat_with_messages = session.exec(statement).first()

        return chat_with_messages
