from fastapi import APIRouter
from app.router import user

router = APIRouter()
router.include_router(user.auth_router)
router.include_router(user.nonauth_router)
