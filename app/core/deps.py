from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from app.database import get_database
from app.core.security import decode_access_token
from app.crud.user import get_user_by_email
from app.models.user import UserInDB, UserResponse
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_db_client():
    # This dependency provides the AsyncIOMotorClient directly
    # The actual database selection happens in the CRUD functions
    return get_database().client # Access the client from the database object

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_client: Annotated[AsyncIOMotorClient, Depends(get_db_client)]
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    token_data = TokenData(email=email) # Assuming email is the subject in JWT

    user = await get_user_by_email(db_client, email=token_data.email)
    if user is None:
        raise credentials_exception
    return UserResponse(**user.model_dump(by_alias=True)) # Return UserResponse schema

async def get_current_active_user(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user. Please verify your email.")
    return current_user

async def get_current_admin_user(current_user: Annotated[UserResponse, Depends(get_current_active_user)]):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions. Admin access required.")
    return current_user
