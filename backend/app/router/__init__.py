from fastapi import APIRouter
from app.router import user_router, chat_router, document_router
from app.config import settings


router = APIRouter(prefix=settings.API_STR)
router.include_router(user_router.nonauth_router)
router.include_router(chat_router.nonauth_router)
router.include_router(document_router.nonauth_router)
router.include_router(user_router.auth_router)
router.include_router(chat_router.auth_router)
router.include_router(document_router.auth_router)


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {"status": "healthy", "service": "chat-backend", "version": "1.0.0"}


