from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import UserCreate, UserInDB, UserResponse
from app.config import settings
from bson import ObjectId

async def get_user_collection(db_client: AsyncIOMotorClient):
    return db_client[settings.DATABASE_NAME]["users"]

async def create_user(db_client: AsyncIOMotorClient, user: UserInDB):
    users_collection = await get_user_collection(db_client)
    result = await users_collection.insert_one(user.model_dump(by_alias=True, exclude=["id"]))
    user.id = result.inserted_id
    return user

async def get_user_by_email(db_client: AsyncIOMotorClient, email: str) -> UserInDB | None:
    users_collection = await get_user_collection(db_client)
    user_data = await users_collection.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None

async def get_user_by_id(db_client: AsyncIOMotorClient, user_id: str) -> UserInDB | None:
    users_collection = await get_user_collection(db_client)
    user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return UserInDB(**user_data)
    return None

async def get_user_by_student_id(db_client: AsyncIOMotorClient, student_id: str) -> UserInDB | None:
    users_collection = await get_user_collection(db_client)
    user_data = await users_collection.find_one({"studentId": student_id})
    if user_data:
        return UserInDB(**user_data)
    return None

async def update_user(db_client: AsyncIOMotorClient, user_id: str, data: dict):
    users_collection = await get_user_collection(db_client)
    await users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    updated_user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
    if updated_user_data:
        return UserInDB(**updated_user_data)
    return None

# Add more CRUD functions as needed for admin, e.g., get_all_users
async def get_all_users(db_client: AsyncIOMotorClient):
    users_collection = await get_user_collection(db_client)
    users_cursor = users_collection.find({})
    users_list = []
    async for user_data in users_cursor:
        users_list.append(UserResponse(**user_data))
    return users_list
