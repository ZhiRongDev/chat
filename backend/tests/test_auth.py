"""
Tests for authentication endpoints and functionality.
"""
import pytest
from fastapi.testclient import TestClient
from app.auth import create_access_token, verify_access_token, CreateAccessTokenPayload
from datetime import timedelta


def test_create_access_token():
    """Test JWT token creation."""
    payload = CreateAccessTokenPayload(sub="testuser")
    token = create_access_token(payload)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_access_token():
    """Test JWT token verification."""
    payload = CreateAccessTokenPayload(sub="testuser")
    token = create_access_token(payload)

    decoded = verify_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


def test_create_reset_token():
    """Test password reset token creation."""
    payload = CreateAccessTokenPayload(sub="testuser", reset=True)
    token = create_access_token(payload, expires_delta=timedelta(hours=1))

    decoded = verify_access_token(token)

    assert decoded["sub"] == "testuser"
    assert decoded["reset"] == True


def test_register(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/user/register",
        json={
            "username": "newuser",
            "password": "newpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_username(client: TestClient):
    """Test registration with duplicate username."""
    # Register first user
    client.post(
        "/api/v1/user/register",
        json={
            "username": "duplicate",
            "password": "password123",
        },
    )

    # Try to register same username again
    response = client.post(
        "/api/v1/user/register",
        json={
            "username": "duplicate",
            "password": "password456",
        },
    )

    assert response.status_code == 409
    assert "already exist" in response.json()["detail"].lower()


def test_login(client: TestClient):
    """Test user login."""
    # First register a user
    client.post(
        "/api/v1/user/register",
        json={
            "username": "loginuser",
            "password": "loginpass123",
        },
    )

    # Then try to login
    response = client.post(
        "/api/v1/user/login",
        json={
            "username": "loginuser",
            "password": "loginpass123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "loginuser"


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/user/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


def test_forgot_password(client: TestClient):
    """Test forgot password endpoint."""
    # First register a user
    client.post(
        "/api/v1/user/register",
        json={
            "username": "forgotuser",
            "password": "oldpassword",
        },
    )

    # Request password reset
    response = client.post(
        "/api/v1/user/forgot-password",
        json={
            "username": "forgotuser",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "token" in data["message"].lower() or "generated" in data["message"].lower()


def test_reset_password(client: TestClient):
    """Test password reset endpoint."""
    # Register a user
    client.post(
        "/api/v1/user/register",
        json={
            "username": "resetuser",
            "password": "oldpassword",
        },
    )

    # Request reset token
    reset_response = client.post(
        "/api/v1/user/forgot-password",
        json={
            "username": "resetuser",
        },
    )

    # Extract token from message (dev mode)
    message = reset_response.json()["message"]
    token = message.split(": ")[-1] if ": " in message else None

    if token:
        # Reset password with token
        response = client.post(
            "/api/v1/user/reset-password",
            json={
                "token": token,
                "new_password": "newpassword123",
            },
        )

        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

        # Try to login with new password
        login_response = client.post(
            "/api/v1/user/login",
            json={
                "username": "resetuser",
                "password": "newpassword123",
            },
        )

        assert login_response.status_code == 200


def test_get_current_user(client: TestClient):
    """Test getting current user info."""
    # Register and login
    client.post(
        "/api/v1/user/register",
        json={
            "username": "currentuser",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/api/v1/user/login",
        json={
            "username": "currentuser",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/user/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert "password" not in data


def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/user/")

    assert response.status_code == 401
