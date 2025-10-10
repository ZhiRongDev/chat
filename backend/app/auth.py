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


class VerifyAccessTokenReturn(BaseModel):
    username: str
    expires: int


def create_access_token(data: CreateAccessTokenPayload) -> str:
    to_encode = data.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.EXPIRES_DELTA)
    to_encode.update({"exp": expire})  # add expiration
    access_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return access_token


def verify_access_token(token: str) -> VerifyAccessTokenReturn:
    result: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    username = result.get("sub")
    expires = result.get("exp")
    return VerifyAccessTokenReturn(username=username, expires=expires)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_info: VerifyAccessTokenReturn = verify_access_token(token)
    user_service = UserService()
    user = user_service.get_user_by_username(token_info.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user
