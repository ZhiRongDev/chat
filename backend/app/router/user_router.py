from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, field_serializer
from app.model import User
from app.service.user_service import UserService
from app.auth import get_current_user, create_access_token, CreateAccessTokenPayload
from app.error import ErrorCode

auth_router = APIRouter(
    prefix="/user", tags=["user"], dependencies=[Depends(get_current_user)]
)
nonauth_router = APIRouter(prefix="/user", tags=["user"])


class UserPayload(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str  # Snowflake ID as string for JavaScript safety
    username: str
    created_at: int

    @field_serializer('id')
    def serialize_id(self, value: int | str, _info) -> str:
        """Convert ID to string for frontend"""
        return str(value)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# While setting response_model, it will only return the fields specified in the model.
@auth_router.get("/", response_model=UserResponse)
async def user(current_user: User = Depends(get_current_user)):
    return current_user


@nonauth_router.post("/register", response_model=UserResponse)
async def register(payload: UserPayload):
    """
    Register a new user account.

    - **username**: Unique username for the account
    - **password**: Password for the account (will be hashed)

    Returns the created user information.
    """
    user_service = UserService()

    if user_service.get_user_by_username(payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.USER_ALREADY_EXIST
        )

    user_to_create = User(
        username=payload.username,
        password=user_service.hash_the_password(payload.password),
        is_superuser=False,
    )

    user_created = user_service.create_user(user_to_create)
    user_created.id = str(user_created.id)
    return user_created


@nonauth_router.post("/login", response_model=LoginResponse)
async def login(payload: UserPayload):
    """
    Login with username and password.

    - **username**: Your username
    - **password**: Your password

    Returns an access token and user information.
    """
    user_service = UserService()

    user = user_service.get_user_by_username(payload.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.INVALID_CREDENTIALS,
        )

    if not user_service.verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.INVALID_CREDENTIALS,
        )

    access_token = create_access_token(CreateAccessTokenPayload(sub=user.username))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(id=str(user.id), username=user.username, created_at=user.created_at),
    )
