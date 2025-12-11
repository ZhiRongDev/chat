import jwt
from app.config import settings
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Cookie
from app.service.user_service import UserService
from typing import Optional


class CreateAccessTokenPayload(BaseModel):
    sub: str  # username
    reset: bool = False  # Flag for password reset tokens
    verify: bool = False  # Flag for email verification tokens


class VerifyAccessTokenReturn(BaseModel):
    username: str
    expires: int


def create_access_token(
    data: CreateAccessTokenPayload,
    expires_delta: timedelta | None = None
) -> str:
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.EXPIRES_DELTA)
    to_encode.update({"exp": expire})  # add expiration
    access_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return access_token


def verify_access_token(token: str) -> dict:
    """Verify token and return all claims as dict."""
    result: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    return result


async def get_current_user(sessionId: Optional[str] = Cookie(None)):
    """
    Get current user from session cookie.

    Args:
        sessionId: JWT token from httpOnly cookie

    Returns:
        User object if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    if not sessionId:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        token_data = verify_access_token(sessionId)
        username = token_data.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user_service = UserService()
        user = user_service.get_user_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )


async def get_current_user_optional(sessionId: Optional[str] = Cookie(None)):
    """
    Get current user from session cookie, but return None if not authenticated.
    Used for endpoints that support both authenticated and non-authenticated access.

    Args:
        sessionId: JWT token from httpOnly cookie

    Returns:
        User object if authenticated, None otherwise
    """
    if not sessionId:
        return None

    try:
        token_data = verify_access_token(sessionId)
        username = token_data.get("sub")
        if not username:
            return None
        user_service = UserService()
        user = user_service.get_user_by_username(username)
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
