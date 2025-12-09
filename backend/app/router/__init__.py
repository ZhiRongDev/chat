from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.router import user_router, chat_router, document_router
from app.service.user_service import UserService
from app.auth import create_access_token, CreateAccessTokenPayload
from pydantic import BaseModel
from app.config import settings


router = APIRouter(prefix=settings.API_STR)
router.include_router(user_router.nonauth_router)
router.include_router(chat_router.nonauth_router)
router.include_router(document_router.nonauth_router)
router.include_router(user_router.auth_router)
router.include_router(chat_router.auth_router)
router.include_router(document_router.auth_router)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {"status": "healthy", "service": "chat-backend", "version": "1.0.0"}


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user_service = UserService()
    user = user_service.get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user_service.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(CreateAccessTokenPayload(sub=user.username)),
        token_type="bearer",
    )
