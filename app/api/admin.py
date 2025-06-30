from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.deps import get_current_admin_user, get_db_client
from app.models.user import UserResponse
from app.crud.user import get_all_users

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=list[UserResponse])
async def get_all_system_users(
    current_admin_user: UserResponse = Depends(get_current_admin_user),
    db_client: AsyncIOMotorClient = Depends(get_db_client)
):
    """
    Retrieve all user details. Only accessible by admin users.
    """
    users = await get_all_users(db_client)
    return users

# Add endpoints for deactivating users, changing roles, etc.
# @router.put("/users/{user_id}/deactivate")
# async def deactivate_user(...):
#     pass
