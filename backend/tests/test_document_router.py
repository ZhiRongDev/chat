"""
Tests for document router endpoints.
"""
import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from app.model.document_model import Document, GeminiFileSearchStore


# ============================================================================
# Document Upload Tests
# ============================================================================


@pytest.mark.integration
def test_upload_document_unauthorized(client: TestClient):
    """Test uploading a document without authentication."""
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"test content", "text/plain")},
    )

    assert response.status_code == 401


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_upload_document_success(mock_service, client: TestClient, auth_headers: dict):
    """Test successful document upload."""
    # Mock the service
    mock_instance = mock_service.return_value
    mock_store = MagicMock(spec=GeminiFileSearchStore)
    mock_store.id = 1
    mock_instance.get_or_create_user_store.return_value = mock_store

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = 123
    mock_doc.filename = "test.txt"
    mock_doc.file_type = "text/plain"
    mock_doc.file_size = 100
    mock_doc.status = "completed"
    mock_doc.gemini_file_id = "file-123"
    mock_instance.upload_file_to_store.return_value = mock_doc

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("test.txt", b"test content", "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["file_type"] == "text/plain"
    assert data["status"] == "completed"
    assert "id" in data


@pytest.mark.integration
def test_upload_document_missing_filename(client: TestClient, auth_headers: dict):
    """Test uploading a document without filename."""
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("", b"test content", "text/plain")},
    )

    # FastAPI will reject empty filename
    assert response.status_code in [400, 422]


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_upload_document_size_limit(mock_service, client: TestClient, auth_headers: dict):
    """Test uploading a document that exceeds size limit."""
    # Create a large file (>100MB)
    large_content = b"x" * (101 * 1024 * 1024)

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("large.txt", large_content, "text/plain")},
    )

    assert response.status_code == 413
    assert "size exceeds" in response.json()["detail"].lower()


# ============================================================================
# Text Ingestion Tests
# ============================================================================


@pytest.mark.integration
def test_ingest_text_unauthorized(client: TestClient):
    """Test text ingestion without authentication."""
    response = client.post(
        "/api/v1/documents/ingest/text",
        json={"title": "Test", "content": "Test content"},
    )

    assert response.status_code == 401


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_ingest_text_success(mock_service, client: TestClient, auth_headers: dict):
    """Test successful text ingestion."""
    # Mock the service
    mock_instance = mock_service.return_value
    mock_store = MagicMock(spec=GeminiFileSearchStore)
    mock_store.id = 1
    mock_instance.get_or_create_user_store.return_value = mock_store

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = 123
    mock_doc.filename = "Test Document.txt"
    mock_doc.file_type = "text/plain"
    mock_doc.file_size = 100
    mock_doc.status = "completed"
    mock_doc.gemini_file_id = "file-123"
    mock_instance.upload_file_to_store.return_value = mock_doc

    response = client.post(
        "/api/v1/documents/ingest/text",
        headers=auth_headers,
        json={
            "title": "Test Document",
            "content": "This is test content for ingestion.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "Test" in data["filename"]
    assert data["status"] == "completed"


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_ingest_text_with_metadata(mock_service, client: TestClient, auth_headers: dict):
    """Test text ingestion with custom metadata."""
    # Mock the service
    mock_instance = mock_service.return_value
    mock_store = MagicMock(spec=GeminiFileSearchStore)
    mock_store.id = 1
    mock_instance.get_or_create_user_store.return_value = mock_store

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = 123
    mock_doc.filename = "Test.txt"
    mock_doc.file_type = "text/plain"
    mock_doc.file_size = 100
    mock_doc.status = "completed"
    mock_doc.gemini_file_id = "file-123"
    mock_instance.upload_file_to_store.return_value = mock_doc

    response = client.post(
        "/api/v1/documents/ingest/text",
        headers=auth_headers,
        json={
            "title": "Test",
            "content": "Content",
            "metadata": {"category": "test", "importance": "high"},
        },
    )

    assert response.status_code == 200


# ============================================================================
# URL Ingestion Tests
# ============================================================================


@pytest.mark.integration
def test_ingest_url_unauthorized(client: TestClient):
    """Test URL ingestion without authentication."""
    response = client.post(
        "/api/v1/documents/ingest/url",
        json={"url": "https://example.com/document.pdf"},
    )

    assert response.status_code == 401


@pytest.mark.integration
@patch("app.router.document_router.requests.get")
@patch("app.router.document_router.GeminiFileSearchService")
def test_ingest_url_success(mock_service, mock_get, client: TestClient, auth_headers: dict):
    """Test successful URL ingestion."""
    # Mock the HTTP request
    mock_response = Mock()
    mock_response.content = b"PDF content here"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    # Mock the service
    mock_instance = mock_service.return_value
    mock_store = MagicMock(spec=GeminiFileSearchStore)
    mock_store.id = 1
    mock_instance.get_or_create_user_store.return_value = mock_store

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = 123
    mock_doc.filename = "document.pdf"
    mock_doc.file_type = "application/pdf"
    mock_doc.file_size = 100
    mock_doc.status = "completed"
    mock_doc.gemini_file_id = "file-123"
    mock_instance.upload_file_to_store.return_value = mock_doc

    response = client.post(
        "/api/v1/documents/ingest/url",
        headers=auth_headers,
        json={"url": "https://example.com/document.pdf"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "document.pdf" in data["filename"]


@pytest.mark.integration
@patch("app.router.document_router.requests.get")
def test_ingest_url_download_failure(mock_get, client: TestClient, auth_headers: dict):
    """Test URL ingestion when download fails."""
    # Mock failed HTTP request
    import requests
    mock_get.side_effect = requests.RequestException("Connection timeout")

    response = client.post(
        "/api/v1/documents/ingest/url",
        headers=auth_headers,
        json={"url": "https://example.com/document.pdf"},
    )

    assert response.status_code == 400
    assert "download" in response.json()["detail"].lower()


# ============================================================================
# Document List and Retrieval Tests
# ============================================================================


@pytest.mark.integration
def test_list_documents_unauthorized(client: TestClient):
    """Test listing documents without authentication."""
    response = client.get("/api/v1/documents/")

    assert response.status_code == 401


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_list_documents_empty(mock_service, client: TestClient, auth_headers: dict):
    """Test listing documents when user has none."""
    # Mock empty list
    mock_instance = mock_service.return_value
    mock_instance.list_documents.return_value = []

    response = client.get(
        "/api/v1/documents/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_list_documents_with_pagination(mock_service, client: TestClient, auth_headers: dict):
    """Test listing documents with pagination parameters."""
    # Mock document list
    mock_instance = mock_service.return_value
    mock_docs = []
    for i in range(5):
        mock_doc = MagicMock(spec=Document)
        mock_doc.id = i
        mock_doc.filename = f"doc{i}.txt"
        mock_doc.file_type = "text/plain"
        mock_doc.file_size = 100
        mock_doc.status = "completed"
        mock_doc.gemini_file_id = f"file-{i}"
        mock_doc.created_at = 1000000 + i
        mock_doc.updated_at = 1000000 + i
        mock_docs.append(mock_doc)

    mock_instance.list_documents.return_value = mock_docs[:3]  # Return only 3

    response = client.get(
        "/api/v1/documents/?limit=3&offset=0",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


@pytest.mark.integration
def test_get_document_unauthorized(client: TestClient):
    """Test getting document details without authentication."""
    response = client.get("/api/v1/documents/123")

    assert response.status_code == 401


@pytest.mark.integration
def test_get_document_invalid_id(client: TestClient, auth_headers: dict):
    """Test getting document with invalid ID format."""
    response = client.get(
        "/api/v1/documents/invalid_id",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.integration
def test_get_nonexistent_document(client: TestClient, auth_headers: dict):
    """Test getting a document that doesn't exist."""
    response = client.get(
        "/api/v1/documents/999999999",
        headers=auth_headers,
    )

    assert response.status_code == 404


# ============================================================================
# Document Deletion Tests
# ============================================================================


@pytest.mark.integration
def test_delete_document_unauthorized(client: TestClient):
    """Test deleting document without authentication."""
    response = client.delete("/api/v1/documents/123")

    assert response.status_code == 401


@pytest.mark.integration
def test_delete_document_invalid_id(client: TestClient, auth_headers: dict):
    """Test deleting document with invalid ID format."""
    response = client.delete(
        "/api/v1/documents/invalid_id",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.integration
def test_delete_nonexistent_document(client: TestClient, auth_headers: dict):
    """Test deleting a document that doesn't exist."""
    response = client.delete(
        "/api/v1/documents/999999999",
        headers=auth_headers,
    )

    assert response.status_code == 404


# ============================================================================
# Document Statistics Tests
# ============================================================================


@pytest.mark.integration
def test_get_document_stats_unauthorized(client: TestClient):
    """Test getting document stats without authentication."""
    response = client.get("/api/v1/documents/stats/overview")

    assert response.status_code == 401


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_get_document_stats_empty(mock_service, client: TestClient, auth_headers: dict):
    """Test getting document stats when user has no documents."""
    # Mock empty list
    mock_instance = mock_service.return_value
    mock_instance.list_documents.return_value = []

    response = client.get(
        "/api/v1/documents/stats/overview",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 0
    assert data["total_size_bytes"] == 0
    assert data["documents_by_type"] == {}


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_get_document_stats_with_documents(mock_service, client: TestClient, auth_headers: dict):
    """Test getting document stats with multiple documents."""
    # Mock document list with different types
    mock_instance = mock_service.return_value
    mock_docs = []

    # Create 3 PDFs and 2 TXTs
    for i in range(3):
        mock_doc = MagicMock(spec=Document)
        mock_doc.file_type = "application/pdf"
        mock_doc.file_size = 1000
        mock_docs.append(mock_doc)

    for i in range(2):
        mock_doc = MagicMock(spec=Document)
        mock_doc.file_type = "text/plain"
        mock_doc.file_size = 500
        mock_docs.append(mock_doc)

    mock_instance.list_documents.return_value = mock_docs

    response = client.get(
        "/api/v1/documents/stats/overview",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 5
    assert data["total_size_bytes"] == 4000  # (3*1000) + (2*500)
    assert data["documents_by_type"]["application/pdf"] == 3
    assert data["documents_by_type"]["text/plain"] == 2


# ============================================================================
# Store Information Tests
# ============================================================================


@pytest.mark.integration
def test_get_store_info_unauthorized(client: TestClient):
    """Test getting store info without authentication."""
    response = client.get("/api/v1/documents/stores/info")

    assert response.status_code == 401


@pytest.mark.integration
@patch("app.router.document_router.GeminiFileSearchService")
def test_get_store_info_success(mock_service, client: TestClient, auth_headers: dict):
    """Test getting store info successfully."""
    # Mock the store
    mock_instance = mock_service.return_value
    mock_store = MagicMock(spec=GeminiFileSearchStore)
    mock_store.id = 1
    mock_store.display_name = "User Store"
    mock_store.description = "User's document store"
    mock_store.document_count = 5
    mock_store.total_size_bytes = 10000
    mock_store.created_at = 1000000
    mock_instance.get_or_create_user_store.return_value = mock_store

    response = client.get(
        "/api/v1/documents/stores/info",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "User Store"
    assert data["document_count"] == 5
    assert data["total_size_bytes"] == 10000
    assert "id" in data
    assert "created_at" in data
