# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.deps import get_db_client, get_current_active_user
from app.core.security import (
    get_password_hash, create_access_token, verify_password,
    create_verification_token, verify_and_decode_token
)
from app.crud.user import create_user, get_user_by_email, get_user_by_student_id, update_user
from app.models.user import UserCreate, UserInDB, UserResponse
from app.schemas.auth import Token, ForgotPasswordRequest, ResetPasswordRequest
from datetime import timedelta
from app.config import settings
from app.core.email import send_verification_email, send_password_reset_email
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Helper function for frontend URL generation ---
def get_frontend_base_url(request: Request) -> str:
    # In production, this should be explicitly set via an environment variable
    # like settings.FRONTEND_BASE_URL for security and reliability.
    # For local development, this tries to guess from the request.
    if settings.FRONTEND_BASE_URL:
        return settings.FRONTEND_BASE_URL
    return str(request.base_url).rstrip('/')

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, # Non-default argument
    background_tasks: BackgroundTasks, # Non-default argument
    request: Request, # Non-default argument
    db_client: AsyncIOMotorClient = Depends(get_db_client) # Default argument (must come last)
):
    """
    Registers a new user. Sends a verification email.
    """
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")

    db_user = await get_user_by_email(db_client, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    db_user = await get_user_by_student_id(db_client, student_id=user_data.student_id)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student ID already registered.")

    hashed_password = get_password_hash(user_data.password)
    user_in_db = UserInDB(**user_data.model_dump(exclude=["password", "confirm_password"]), hashed_password=hashed_password)
    # is_active is False by default, requiring email verification

    new_user = await create_user(db_client, user_in_db)

    # Generate verification token and link
    verification_token = create_verification_token(new_user.email, "email_verification", expires_delta=timedelta(hours=24))
    # Frontend will have a route like /verify-email?token=...
    frontend_base_url = get_frontend_base_url(request)
    verification_link = f"{frontend_base_url}/verify-email?token={verification_token}"

    # Send email in background to not block the API response
    background_tasks.add_task(send_verification_email, new_user.email, new_user.firstname, verification_link)

    logger.info(f"User {new_user.email} registered. Verification email sent.")
    return UserResponse(**new_user.model_dump(by_alias=True))

@router.get("/verify-email", summary="Verify User Email Address")
async def verify_email(token: str, db_client: AsyncIOMotorClient = Depends(get_db_client)):
    """
    Verifies a user's email address using a token received via email.
    """
    payload = verify_and_decode_token(token, "email_verification")
    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token.")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token data missing email.")

    user = await get_user_by_email(db_client, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified.")

    # Activate the user
    updated_user = await update_user(db_client, str(user.id), {"is_active": True})
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate user.")

    logger.info(f"User {email} successfully verified email.")
    return {"message": "Email verified successfully! You can now log in."}

@router.post("/token", response_model=Token, summary="Login and get JWT Token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_client: AsyncIOMotorClient = Depends(get_db_client)
):
    """
    Authenticates a user and returns a JWT access token.
    Uses email as the username for login.
    """
    user = await get_user_by_email(db_client, email=form_data.username) # Using email as username for login
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account not active. Please verify your email.")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"User {user.email} successfully logged in.")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password", status_code=status.HTTP_200_OK, summary="Request Password Reset")
async def forgot_password(
    request_data: ForgotPasswordRequest, # Non-default argument
    background_tasks: BackgroundTasks, # Non-default argument
    request: Request,                  # Non-default argument
    db_client: AsyncIOMotorClient = Depends(get_db_client) # Default argument (must come last)
):
    """
    Initiates the password reset process. Sends a reset link to the user's email.
    """
    user = await get_user_by_email(db_client, email=request_data.email)
    if not user:
        # For security, always return a success message even if email isn't found
        # to prevent enumeration of existing user accounts.
        logger.warning(f"Password reset requested for non-existent email: {request_data.email}")
        return {"message": "If an account with that email exists, a password reset link has been sent."}

    # Generate password reset token
    reset_token = create_verification_token(user.email, "password_reset", expires_delta=timedelta(minutes=60))
    # Frontend will have a route like /reset-password?token=...
    frontend_base_url = get_frontend_base_url(request)
    reset_link = f"{frontend_base_url}/reset-password?token={reset_token}"

    # Send email in background
    background_tasks.add_task(send_password_reset_email, user.email, user.firstname, reset_link)

    logger.info(f"Password reset link sent to {user.email}.")
    return {"message": "If an account with that email exists, a password reset link has been sent."}

@router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Reset Password with Token")
async def reset_password(
    reset_data: ResetPasswordRequest,
    db_client: AsyncIOMotorClient = Depends(get_db_client)
):
    """
    Resets the user's password using a valid reset token.
    """
    if reset_data.new_password != reset_data.confirm_new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match.")

    # Decode and verify the reset token
    payload = verify_and_decode_token(reset_data.token, "password_reset")
    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token.")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token data missing email.")

    user = await get_user_by_email(db_client, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Update password
    hashed_new_password = get_password_hash(reset_data.new_password)
    updated_user = await update_user(db_client, str(user.id), {"hashed_password": hashed_new_password})

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password.")

    logger.info(f"Password for {email} successfully reset.")
    return {"message": "Password has been reset successfully. You can now log in with your new password."}

@router.get("/me", response_model=UserResponse, summary="Get Current User Details")
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    """
    Retrieves details of the currently authenticated active user.
    """
    return current_user
 