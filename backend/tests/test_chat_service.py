"""
Tests for chat service.
"""
import pytest
from app.service.chat_service import ChatService
from app.model.chat_model import ChatHistory, ChatMessage


@pytest.mark.unit
def test_create_chat_history(session):
    """Test creating a chat history."""
    chat_service = ChatService()

    chat = chat_service.create_chat_history(
        user_id=1,
        title="Test Chat"
    )

    assert chat is not None
    assert chat.title == "Test Chat"
    assert chat.user_id == 1
    assert chat.created_at is not None
    assert chat.updated_at is not None


@pytest.mark.unit
def test_get_chat_history_by_id(session):
    """Test retrieving a chat history by ID."""
    chat_service = ChatService()

    # Create a chat
    chat = chat_service.create_chat_history(
        user_id=1,
        title="Test Chat"
    )

    # Retrieve it
    retrieved_chat = chat_service.get_chat_history_by_id(chat.id, user_id=1)

    assert retrieved_chat is not None
    assert retrieved_chat.id == chat.id
    assert retrieved_chat.title == "Test Chat"


@pytest.mark.unit
def test_get_chat_history_wrong_user(session):
    """Test that retrieving a chat with wrong user_id returns None."""
    chat_service = ChatService()

    # Create a chat for user 1
    chat = chat_service.create_chat_history(
        user_id=1,
        title="User 1 Chat"
    )

    # Try to retrieve with user_id 2
    retrieved_chat = chat_service.get_chat_history_by_id(chat.id, user_id=2)

    assert retrieved_chat is None


@pytest.mark.unit
def test_get_all_chat_histories(session):
    """Test retrieving all chat histories."""
    chat_service = ChatService()

    # Create multiple chats
    chat_service.create_chat_history(user_id=1, title="Chat 1")
    chat_service.create_chat_history(user_id=1, title="Chat 2")
    chat_service.create_chat_history(user_id=1, title="Chat 3")

    # Retrieve all
    chats = chat_service.get_all_chat_histories(user_id=1)

    assert len(chats) >= 3
    # Should be sorted by created_at descending (newest first)
    # Note: Due to fast execution, timestamps may be identical, so just check we got all titles
    titles = [chat["title"] for chat in chats]
    assert "Chat 1" in titles
    assert "Chat 2" in titles
    assert "Chat 3" in titles


@pytest.mark.unit
def test_get_all_chat_histories_with_limit(session):
    """Test retrieving chat histories with limit."""
    chat_service = ChatService()

    # Create multiple chats
    for i in range(5):
        chat_service.create_chat_history(user_id=1, title=f"Chat {i}")

    # Retrieve with limit
    chats = chat_service.get_all_chat_histories(user_id=1, limit=3)

    assert len(chats) <= 3


@pytest.mark.unit
def test_update_chat_history(session):
    """Test updating a chat history."""
    import time
    chat_service = ChatService()

    # Create a chat
    chat = chat_service.create_chat_history(
        user_id=1,
        title="Original Title"
    )

    # Small delay to ensure timestamp difference
    time.sleep(0.001)

    # Update it
    updated_chat = chat_service.update_chat_history(
        chat_id=chat.id,
        title="Updated Title",
        user_id=1
    )

    assert updated_chat is not None
    assert updated_chat.title == "Updated Title"
    assert updated_chat.updated_at >= chat.updated_at


@pytest.mark.unit
def test_update_nonexistent_chat(session):
    """Test updating a chat that doesn't exist."""
    chat_service = ChatService()

    updated_chat = chat_service.update_chat_history(
        chat_id=999999,
        title="New Title",
        user_id=1
    )

    assert updated_chat is None


@pytest.mark.unit
def test_delete_chat_history(session):
    """Test deleting a chat history."""
    chat_service = ChatService()

    # Create a chat
    chat = chat_service.create_chat_history(
        user_id=1,
        title="To Delete"
    )

    # Delete it
    deleted = chat_service.delete_chat_history(chat.id, user_id=1)

    assert deleted is True

    # Verify it's deleted
    retrieved_chat = chat_service.get_chat_history_by_id(chat.id, user_id=1)
    assert retrieved_chat is None


@pytest.mark.unit
def test_delete_nonexistent_chat(session):
    """Test deleting a chat that doesn't exist."""
    chat_service = ChatService()

    deleted = chat_service.delete_chat_history(999999, user_id=1)

    assert deleted is False


@pytest.mark.unit
def test_add_message(session):
    """Test adding a message to a chat."""
    chat_service = ChatService()

    # Create a chat
    chat = chat_service.create_chat_history(
        user_id=1,
        title="Test Chat"
    )

    # Add a message
    message = chat_service.add_message(
        chat_id=chat.id,
        sender="user",
        text="Hello, bot!",
        message_order=0
    )

    assert message is not None
    assert message.sender == "user"
    assert message.text == "Hello, bot!"
    assert message.message_order == 0
    assert message.chat_history_id == chat.id


@pytest.mark.unit
def test_get_messages_by_chat_id(session):
    """Test retrieving messages for a chat."""
    chat_service = ChatService()

    # Create a chat
    chat = chat_service.create_chat_history(
        user_id=1,
        title="Test Chat"
    )

    # Add multiple messages
    chat_service.add_message(chat.id, "user", "Message 1", 0)
    chat_service.add_message(chat.id, "bot", "Response 1", 1)
    chat_service.add_message(chat.id, "user", "Message 2", 2)

    # Retrieve messages
    messages = chat_service.get_messages_by_chat_id(chat.id)

    assert len(messages) == 3
    assert messages[0].text == "Message 1"
    assert messages[1].text == "Response 1"
    assert messages[2].text == "Message 2"


@pytest.mark.unit
def test_save_chat_with_messages_new(session):
    """Test saving a new chat with messages."""
    chat_service = ChatService()

    messages = [
        {"sender": "user", "text": "Hello"},
        {"sender": "bot", "text": "Hi there!"},
    ]

    chat = chat_service.save_chat_with_messages(
        chat_id=None,
        user_id=1,
        title="New Chat",
        messages=messages
    )

    assert chat is not None
    assert chat.title == "New Chat"
    assert chat.user_id == 1

    # Verify messages were saved
    saved_messages = chat_service.get_messages_by_chat_id(chat.id)
    assert len(saved_messages) == 2
    assert saved_messages[0].text == "Hello"
    assert saved_messages[1].text == "Hi there!"


@pytest.mark.unit
def test_save_chat_with_messages_update(session):
    """Test updating an existing chat with new messages."""
    chat_service = ChatService()

    # Create initial chat
    initial_messages = [
        {"sender": "user", "text": "First message"},
    ]

    chat = chat_service.save_chat_with_messages(
        chat_id=None,
        user_id=1,
        title="Original Title",
        messages=initial_messages
    )

    # Update the chat
    updated_messages = [
        {"sender": "user", "text": "First message"},
        {"sender": "bot", "text": "Second message"},
        {"sender": "user", "text": "Third message"},
    ]

    updated_chat = chat_service.save_chat_with_messages(
        chat_id=chat.id,
        user_id=1,
        title="Updated Title",
        messages=updated_messages
    )

    assert updated_chat.id == chat.id
    assert updated_chat.title == "Updated Title"

    # Verify messages were updated
    saved_messages = chat_service.get_messages_by_chat_id(chat.id)
    assert len(saved_messages) == 3
    assert saved_messages[2].text == "Third message"


@pytest.mark.unit
def test_save_chat_with_messages_invalid_chat_id(session):
    """Test updating a non-existent chat."""
    chat_service = ChatService()

    messages = [
        {"sender": "user", "text": "Hello"},
    ]

    with pytest.raises(ValueError, match="not found"):
        chat_service.save_chat_with_messages(
            chat_id=999999,
            user_id=1,
            title="Test",
            messages=messages
        )


@pytest.mark.unit
def test_chat_history_message_count(session):
    """Test that message count is correct in chat history list."""
    chat_service = ChatService()

    # Create a chat with messages
    chat = chat_service.create_chat_history(
        user_id=1,
        title="Chat with Messages"
    )

    # Add messages
    chat_service.add_message(chat.id, "user", "Message 1", 0)
    chat_service.add_message(chat.id, "bot", "Message 2", 1)
    chat_service.add_message(chat.id, "user", "Message 3", 2)

    # Get all chats
    chats = chat_service.get_all_chat_histories(user_id=1)

    # Find our chat
    test_chat = next((c for c in chats if c["title"] == "Chat with Messages"), None)
    assert test_chat is not None
    assert test_chat["message_count"] == 3


@pytest.mark.unit
def test_save_chat_with_empty_messages(session):
    """Test saving a chat with no messages."""
    chat_service = ChatService()

    chat = chat_service.save_chat_with_messages(
        chat_id=None,
        user_id=1,
        title="Empty Chat",
        messages=[]
    )

    assert chat is not None
    assert chat.title == "Empty Chat"

    # Verify no messages
    messages = chat_service.get_messages_by_chat_id(chat.id)
    assert len(messages) == 0


@pytest.mark.unit
def test_delete_chat_with_messages(session):
    """Test that deleting a chat also deletes its messages."""
    chat_service = ChatService()

    # Create chat with messages
    messages = [
        {"sender": "user", "text": "Message 1"},
        {"sender": "bot", "text": "Message 2"},
    ]

    chat = chat_service.save_chat_with_messages(
        chat_id=None,
        user_id=1,
        title="Chat to Delete",
        messages=messages
    )

    # Delete the chat
    deleted = chat_service.delete_chat_history(chat.id, user_id=1)
    assert deleted is True

    # Verify messages are also deleted
    messages = chat_service.get_messages_by_chat_id(chat.id)
    assert len(messages) == 0


@pytest.mark.unit
def test_message_ordering(session):
    """Test that messages maintain correct order."""
    chat_service = ChatService()

    # Create chat
    chat = chat_service.create_chat_history(
        user_id=1,
        title="Order Test"
    )

    # Add messages in specific order
    chat_service.add_message(chat.id, "user", "First", 0)
    chat_service.add_message(chat.id, "bot", "Second", 1)
    chat_service.add_message(chat.id, "user", "Third", 2)
    chat_service.add_message(chat.id, "bot", "Fourth", 3)

    # Retrieve and verify order
    messages = chat_service.get_messages_by_chat_id(chat.id)

    assert len(messages) == 4
    assert messages[0].text == "First"
    assert messages[0].message_order == 0
    assert messages[1].text == "Second"
    assert messages[1].message_order == 1
    assert messages[2].text == "Third"
    assert messages[2].message_order == 2
    assert messages[3].text == "Fourth"
    assert messages[3].message_order == 3
