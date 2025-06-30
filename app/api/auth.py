from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.deps import get_current_active_user, get_db_client
from app.core.security import get_password_hash, create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_student_id
from app.models.user import UserCreate, UserInDB, UserResponse
from app.schemas.auth import Token
from datetime import timedelta
from app.config import settings
from app.core.email import send_verification_email # New import for Brevo

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db_client: AsyncIOMotorClient = Depends(get_db_client)):
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

    new_user = await create_user(db_client, user_in_db)

    # Send email verification
    # You might want to generate a unique token for verification and store it in DB
    # For simplicity, we'll just send a general welcome email for now.
    # In a real app, you'd send a link like: your_domain.com/verify?token=XYZ
    verification_link = "http://your_domain.com/verify_email?token=SOME_UNIQUE_TOKEN" # Implement this
    await send_verification_email(new_user.email, new_user.firstname, verification_link)

    return UserResponse(**new_user.model_dump(by_alias=True))

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db_client: AsyncIOMotorClient = Depends(get_db_client)):
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
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user
