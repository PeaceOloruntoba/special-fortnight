from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGO_DETAILS)
    print("Connected to MongoDB!")

async def close_mongo_connection():
    global client
    client.close()
    print("Closed MongoDB connection.")

def get_database():
    return client[settings.DATABASE_NAME]
