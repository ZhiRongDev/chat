from fastapi import APIRouter
from app.router import user_router, chat_router

router = APIRouter()
router.include_router(user_router.auth_router)
router.include_router(user_router.nonauth_router)
router.include_router(chat_router.nonauth_router)
