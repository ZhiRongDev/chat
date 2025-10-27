import jwt
from app.config import settings
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.service.user_service import UserService


# This will check the response of '/api/v1/token'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


class CreateAccessTokenPayload(BaseModel):
    sub: str  # username
    reset: bool = False  # Flag for password reset tokens


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


async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = verify_access_token(token)
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
