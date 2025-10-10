from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.model import User
from app.service.user_service import UserService
from app.auth import get_current_user

auth_router = APIRouter(prefix="/user", tags=["user"], dependencies=[Depends(get_current_user)])
nonauth_router = APIRouter(prefix="/user", tags=["user"])


class UserPayload(BaseModel):
    username: str
    password: str
    is_superuser: bool = False


class UserResponse(BaseModel):
    username: str
    created_at: int


# While setting response_model, it will only return the fields specified in the model.
@auth_router.get("/", response_model=UserResponse)
async def user(current_user: User = Depends(get_current_user)):
    return current_user


@nonauth_router.post("/", response_model=UserResponse)
async def create_user(payload: UserPayload):
    user_service = UserService()

    if user_service.get_user_by_username(payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User Already exist"
        )
    
    user_to_create = User(
        username=payload.username,
        password=user_service.hash_the_password(payload.password),
        is_superuser=payload.is_superuser,
    )

    user_created = user_service.create_user(user_to_create)
    return user_created
