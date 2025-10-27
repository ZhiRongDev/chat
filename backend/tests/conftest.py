"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app import create_app
from app.model import engine as default_engine, User
from app.service.user_service import UserService
from app.auth import create_access_token, CreateAccessTokenPayload


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture():
    """Create a test client for the FastAPI app."""
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user."""
    user_service = UserService()
    user = User(
        username="testuser",
        password=user_service.hash_the_password("testpassword"),
        is_superuser=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Generate an authentication token for the test user."""
    token = create_access_token(CreateAccessTokenPayload(sub=test_user.username))
    return token


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Generate authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}
