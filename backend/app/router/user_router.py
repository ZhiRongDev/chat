from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, field_serializer
from app.model import User
from app.service.user_service import UserService
from app.auth import get_current_user, create_access_token, CreateAccessTokenPayload, verify_access_token
from app.error import ErrorCode
from datetime import timedelta
from app.utils import send_reset_email, send_verification_email
from app.config import settings

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


class MessageResponse(BaseModel):
    message: str


# While setting response_model, it will only return the fields specified in the model.
@auth_router.get("/", response_model=UserResponse)
async def user(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        created_at=current_user.created_at
    )


@nonauth_router.post("/register", response_model=MessageResponse)
async def register(payload: UserPayload):
    """
    Register a new user account.

    - **username**: Unique username (email address) for the account
    - **password**: Password for the account (will be hashed)

    Sends a verification email with a token. User must verify email before logging in.
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
        is_verified=False,
    )

    user_created = user_service.create_user(user_to_create)

    # Generate verification token (valid for 24 hours)
    verification_token = create_access_token(
        CreateAccessTokenPayload(sub=user_created.username, verify=True),
        expires_delta=timedelta(hours=24)
    )

    # Send verification email
    send_verification_email(
        subject="驗證你的電子郵件",
        to_email=payload.username,
        verification_link=f"{settings.FRONTEND_HOST}/verify-email?token={verification_token}&username={payload.username}",
    )

    return MessageResponse(
        message="Registration successful! Please check your email to verify your account."
    )


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

    # Check if user has verified their email
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your email for the verification link.",
        )

    access_token = create_access_token(CreateAccessTokenPayload(sub=user.username))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(id=str(user.id), username=user.username, created_at=user.created_at),
    )


class ForgotPasswordPayload(BaseModel):
    username: str


class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str


class VerifyEmailPayload(BaseModel):
    token: str


@nonauth_router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordPayload):
    """
    Request a password reset token.

    - **username**: Username of the account to reset

    In a production environment, this would send an email with the reset token.
    For now, the token is returned in the response (ONLY FOR DEVELOPMENT).
    """
    user_service = UserService()

    user = user_service.get_user_by_username(payload.username)
    if not user:
        # Don't reveal if user exists or not for security
        return MessageResponse(
            message="If the username exists, a password reset token has been generated."
        )

    # Generate a reset token (valid for 1 hour)
    reset_token = create_access_token(
        CreateAccessTokenPayload(sub=user.username, reset=True),
        expires_delta=timedelta(hours=1)
    )

    send_reset_email(
        subject="忘記密碼",
        to_email=payload.username,
        reset_link=f"{settings.FRONTEND_HOST}/reset-password?token={reset_token}&username={payload.username}",
    )

    return MessageResponse(
        message="Password reset token has been sent to your email."
    )


@nonauth_router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordPayload):
    """
    Reset password using a valid reset token.

    - **token**: The reset token received from forgot-password endpoint
    - **new_password**: The new password to set

    Returns success message if password is reset.
    """
    user_service = UserService()

    try:
        # Verify the reset token
        token_data = verify_access_token(payload.token)
        username = token_data.get('sub')

        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        # Get the user
        user = user_service.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.USER_NOT_FOUND
            )

        # Hash the new password and update
        hashed_password = user_service.hash_the_password(payload.new_password)
        user.password = hashed_password
        user_service.update_user(user)

        return MessageResponse(message="Password has been reset successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


@nonauth_router.post("/verify-email", response_model=MessageResponse)
async def verify_email(payload: VerifyEmailPayload):
    """
    Verify email address using the verification token.

    - **token**: The verification token received via email

    Returns success message if email is verified.
    """
    user_service = UserService()

    try:
        # Verify the token
        token_data = verify_access_token(payload.token)
        username = token_data.get('sub')

        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )

        # Get the user
        user = user_service.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.USER_NOT_FOUND
            )

        # Check if already verified
        if user.is_verified:
            return MessageResponse(message="Email is already verified. You can now log in.")

        # Mark user as verified
        user.is_verified = True
        user_service.update_user(user)

        return MessageResponse(message="Email verified successfully! You can now log in.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
