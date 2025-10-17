from sqlmodel import SQLModel, Field, Column, Relationship
from app.utils import snowflake_generator, get_timestamp
from sqlalchemy import BigInteger, ForeignKey, Text
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.model.user_model import User


class ChatHistory(SQLModel, table=True):
    """Chat conversation history - one record per conversation"""
    __tablename__ = "chat_history"

    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    user_id: Optional[int] = Field(
        sa_column=Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=True),
        default=None,
    )
    title: str = Field(max_length=255)
    created_at: int = Field(default_factory=get_timestamp)
    updated_at: int = Field(default_factory=get_timestamp)

    # Relationships
    messages: list["ChatMessage"] = Relationship(
        back_populates="chat_history",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ChatMessage(SQLModel, table=True):
    """Individual messages within a chat conversation"""
    __tablename__ = "chat_message"

    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    chat_history_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("chat_history.id", ondelete="CASCADE"))
    )
    sender: str = Field(max_length=10)  # 'user' or 'bot'
    text: str = Field(sa_column=Column(Text))
    message_order: int  # To maintain message order within a chat
    created_at: int = Field(default_factory=get_timestamp)

    # Relationships
    chat_history: Optional[ChatHistory] = Relationship(back_populates="messages")
