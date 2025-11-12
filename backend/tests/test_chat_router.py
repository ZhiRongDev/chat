"""
Tests for chat router endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.model.user_model import User
from app.service.user_service import UserService


@pytest.mark.unit
def test_get_chat_status(client: TestClient):
    """Test chat status endpoint."""
    response = client.get("/api/v1/chat/status")

    assert response.status_code == 200
    data = response.json()
    assert "available_providers" in data
    assert "supported_providers" in data
    assert "search_enabled" in data
    assert "default_provider" in data
    assert data["supported_providers"] == ["gemini", "openai", "anthropic"]


@pytest.mark.integration
def test_chat_missing_message(client: TestClient):
    """Test chat endpoint with missing message."""
    response = client.post(
        "/api/v1/chat/",
        json={
            "message": "",
            "provider": "gemini",
        },
    )

    assert response.status_code == 400
    assert "message" in response.json()["detail"].lower()


@pytest.mark.integration
def test_chat_invalid_provider(client: TestClient):
    """Test chat endpoint with invalid provider."""
    response = client.post(
        "/api/v1/chat/",
        json={
            "message": "Hello",
            "provider": "invalid_provider",
        },
    )

    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower()


@pytest.mark.integration
def test_chat_rag_requires_gemini(client: TestClient):
    """Test that RAG mode requires Gemini provider."""
    response = client.post(
        "/api/v1/chat/",
        json={
            "message": "Hello",
            "provider": "openai",
            "use_rag": True,
        },
    )

    assert response.status_code == 400
    assert "gemini" in response.json()["detail"].lower()


# Chat History Tests (Authenticated endpoints)


@pytest.mark.integration
def test_get_chat_histories_unauthorized(client: TestClient):
    """Test getting chat histories without authentication."""
    response = client.get("/api/v1/chat/history")

    assert response.status_code == 401


@pytest.mark.integration
def test_get_chat_histories_empty(client: TestClient, auth_headers: dict):
    """Test getting chat histories when user has no chats."""
    response = client.get(
        "/api/v1/chat/history",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_save_chat_history(client: TestClient, auth_headers: dict):
    """Test saving a new chat history."""
    response = client.post(
        "/api/v1/chat/history",
        headers=auth_headers,
        json={
            "title": "Test Chat",
            "messages": [
                {"sender": "user", "text": "Hello"},
                {"sender": "bot", "text": "Hi there!"},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Chat"
    assert len(data["messages"]) == 2
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.integration
def test_save_and_retrieve_chat_history(client: TestClient, auth_headers: dict):
    """Test saving and then retrieving a chat history."""
    # Save a chat
    save_response = client.post(
        "/api/v1/chat/history",
        headers=auth_headers,
        json={
            "title": "My Chat",
            "messages": [
                {"sender": "user", "text": "Question"},
                {"sender": "bot", "text": "Answer"},
            ],
        },
    )
    assert save_response.status_code == 200
    chat_id = save_response.json()["id"]

    # Retrieve the chat
    get_response = client.get(
        f"/api/v1/chat/history/{chat_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == chat_id
    assert data["title"] == "My Chat"
    assert len(data["messages"]) == 2


@pytest.mark.integration
def test_update_existing_chat_history(client: TestClient, auth_headers: dict):
    """Test updating an existing chat history."""
    # Save initial chat
    save_response = client.post(
        "/api/v1/chat/history",
        headers=auth_headers,
        json={
            "title": "Original Title",
            "messages": [
                {"sender": "user", "text": "First message"},
            ],
        },
    )
    assert save_response.status_code == 200
    chat_id = save_response.json()["id"]

    # Update the chat
    update_response = client.post(
        "/api/v1/chat/history",
        headers=auth_headers,
        json={
            "chat_id": chat_id,
            "title": "Updated Title",
            "messages": [
                {"sender": "user", "text": "First message"},
                {"sender": "bot", "text": "Second message"},
            ],
        },
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == chat_id
    assert data["title"] == "Updated Title"
    assert len(data["messages"]) == 2


@pytest.mark.integration
def test_delete_chat_history(client: TestClient, auth_headers: dict):
    """Test deleting a chat history."""
    # Save a chat
    save_response = client.post(
        "/api/v1/chat/history",
        headers=auth_headers,
        json={
            "title": "To Delete",
            "messages": [
                {"sender": "user", "text": "Message"},
            ],
        },
    )
    assert save_response.status_code == 200
    chat_id = save_response.json()["id"]

    # Delete the chat
    delete_response = client.delete(
        f"/api/v1/chat/history/{chat_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200
    assert "deleted" in delete_response.json()["detail"].lower()

    # Verify chat is deleted
    get_response = client.get(
        f"/api/v1/chat/history/{chat_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.integration
def test_get_nonexistent_chat(client: TestClient, auth_headers: dict):
    """Test retrieving a chat that doesn't exist."""
    response = client.get(
        "/api/v1/chat/history/999999999",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_delete_nonexistent_chat(client: TestClient, auth_headers: dict):
    """Test deleting a chat that doesn't exist."""
    response = client.delete(
        "/api/v1/chat/history/999999999",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_get_chat_with_invalid_id_format(client: TestClient, auth_headers: dict):
    """Test getting a chat with invalid ID format."""
    response = client.get(
        "/api/v1/chat/history/invalid_id",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.integration
def test_delete_chat_with_invalid_id_format(client: TestClient, auth_headers: dict):
    """Test deleting a chat with invalid ID format."""
    response = client.delete(
        "/api/v1/chat/history/invalid_id",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.integration
def test_get_chat_histories_with_limit(client: TestClient, auth_headers: dict):
    """Test getting chat histories with limit parameter."""
    # Create multiple chats
    for i in range(5):
        client.post(
            "/api/v1/chat/history",
            headers=auth_headers,
            json={
                "title": f"Chat {i}",
                "messages": [{"sender": "user", "text": f"Message {i}"}],
            },
        )

    # Get chats with limit
    response = client.get(
        "/api/v1/chat/history?limit=3",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


@pytest.mark.integration
def test_save_chat_with_empty_messages(client: TestClient, auth_headers: dict):
    """Test saving a chat with no messages."""
    response = client.post(
        "/api/v1/chat/history",
        headers=auth_headers,
        json={
            "title": "Empty Chat",
            "messages": [],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Empty Chat"
    assert len(data["messages"]) == 0


@pytest.mark.integration
def test_chat_history_message_count(client: TestClient, auth_headers: dict):
    """Test that chat history returns correct message count."""
    # Save a chat with 3 messages
    client.post(
        "/api/v1/chat/history",
        headers=auth_headers,
        json={
            "title": "Count Test",
            "messages": [
                {"sender": "user", "text": "Message 1"},
                {"sender": "bot", "text": "Message 2"},
                {"sender": "user", "text": "Message 3"},
            ],
        },
    )

    # Get all chats
    response = client.get(
        "/api/v1/chat/history",
        headers=auth_headers,
    )

    assert response.status_code == 200
    chats = response.json()
    # Find our chat
    test_chat = next((c for c in chats if c["title"] == "Count Test"), None)
    assert test_chat is not None
    assert test_chat["message_count"] == 3
