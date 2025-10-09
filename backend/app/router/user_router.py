from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.model import User
from app.service.user_service import UserService

auth_router = APIRouter(prefix="/user", tags=["user"])
nonauth_router = APIRouter(prefix="/user", tags=["user"])


class UserPayload(BaseModel):
    username: str
    password: str
    is_superuser: bool = False

class UserResponse(BaseModel):
    username: str
    created_at: int 


@nonauth_router.get("/")
async def user():
    user_service = UserService() 
    password = "password"
    hashed_password = user_service.hash_the_password(password)
    is_valid = user_service.verify_password(password, hashed_password)
    print(f"hashed_password: {hashed_password}")
    print(f"is_valid: {is_valid}")
    return {"message": "user"}


@nonauth_router.post("/", response_model=UserResponse)
async def create_user(payload: UserPayload):
    user_to_create = User(**payload.model_dump())
    user_service = UserService()

    if (user_service.get_user_by_username(user_to_create.username)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User Already exist")

    user_created = user_service.create_user(user_to_create)
    return user_created
