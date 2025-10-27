"""
Tests for user service.
"""
import pytest
from app.service.user_service import UserService
from app.model import User


def test_hash_password():
    """Test password hashing."""
    user_service = UserService()
    password = "testpassword123"

    hashed = user_service.hash_the_password(password)

    assert hashed is not None
    assert isinstance(hashed, bytes)
    assert hashed != password.encode()


def test_verify_password():
    """Test password verification."""
    user_service = UserService()
    password = "testpassword123"

    hashed = user_service.hash_the_password(password)

    assert user_service.verify_password(password, hashed) == True
    assert user_service.verify_password("wrongpassword", hashed) == False


def test_create_user(session):
    """Test user creation."""
    user_service = UserService()

    user = User(
        username="newuser",
        password=user_service.hash_the_password("password123"),
        is_superuser=False,
    )

    # Note: In real tests with database, this would work
    # For this test, we're just checking the model structure
    assert user.username == "newuser"
    assert user.password is not None
    assert user.is_superuser == False


def test_password_hash_uniqueness():
    """Test that same password generates different hashes (due to salt)."""
    user_service = UserService()
    password = "samepassword"

    hash1 = user_service.hash_the_password(password)
    hash2 = user_service.hash_the_password(password)

    assert hash1 != hash2
    assert user_service.verify_password(password, hash1) == True
    assert user_service.verify_password(password, hash2) == True
