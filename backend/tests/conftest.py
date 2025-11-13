"""
Pytest configuration and fixtures for backend tests.
"""
import os

# Set up test environment variables before importing app
os.environ["TESTING"] = "true"  # Enable test mode
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "0")
os.environ.setdefault("FRONTEND_HOST", "http://localhost:5173")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("EXPIRES_DELTA", "30")
os.environ.setdefault("DEFAULT_LLM_PROVIDER", "gemini")
os.environ.setdefault("GEMINI_FILE_SEARCH_MODEL", "gemini-2.0-flash-exp")
os.environ.setdefault("GEMINI_STORE_SIZE_LIMIT_GB", "20")
os.environ.setdefault("GEMINI_MAX_FILE_SIZE_MB", "100")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app import create_app
from app.auth import create_access_token, CreateAccessTokenPayload


@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Set up a test database for each test function."""
    # Create test database engine
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    # Override the engine in app.model so services use the test database
    import app.model
    original_engine = app.model.engine
    app.model.engine = test_engine

    yield test_engine

    # Restore original engine
    app.model.engine = original_engine


@pytest.fixture(name="session")
def session_fixture(setup_test_database):
    """Create a session for the test database."""
    test_engine = setup_test_database
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(setup_test_database):
    """Create a test client for the FastAPI app with a test database."""
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user in the test database."""
    from app.model import User
    from app.service.user_service import UserService

    user_service = UserService()
    user = User(
        username="testuser",
        password=user_service.hash_the_password("testpassword"),
        is_superuser=False,
        is_verified=True,  # Set verified for tests
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user):
    """Generate an authentication token for the test user."""
    token = create_access_token(CreateAccessTokenPayload(sub=test_user.username))
    return token


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Generate authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}
