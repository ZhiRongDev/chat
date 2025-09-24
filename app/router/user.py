from fastapi import APIRouter
from pydantic import BaseModel
from app.model import User
from app.service.user_service import UserService

auth_router = APIRouter(prefix="/user", tags=["user"])
nonauth_router = APIRouter(prefix="/user", tags=["user"])


class UserPayload(BaseModel):
    username: str
    password: str


@nonauth_router.get("/")
async def user():
    return {"message": "user"}


@nonauth_router.post("/")
async def create_user(payload: UserPayload):
    user_to_create = User(username=payload.username, password=payload.password)
    user_service = UserService()
    user_created = user_service.create_user(user_to_create)
    return user_created
