from fastapi import APIRouter
from app.router import user

router = APIRouter()
router.include_router(user.router)
