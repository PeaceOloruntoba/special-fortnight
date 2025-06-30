# app/api/students.py
from fastapi import APIRouter

router = APIRouter(prefix="/students", tags=["Students"])

# You can add your student-specific endpoints here later, e.g.:
# @router.get("/me", response_model=UserResponse)
# async def read_student_me(current_user: UserResponse = Depends(get_current_active_user)):
#     return current_user

# @router.get("/{student_id}", response_model=UserResponse)
# async def get_student_details(student_id: str, db_client: AsyncIOMotorClient = Depends(get_db_client), current_admin_user: UserResponse = Depends(get_current_admin_user)):
#     # This would be an admin-only endpoint to fetch details of a specific student
#     user = await get_user_by_student_id(db_client, student_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
#     return UserResponse(**user.model_dump(by_alias=True))