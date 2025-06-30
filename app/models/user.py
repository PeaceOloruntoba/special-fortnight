from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId # For handling MongoDB's _id

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(type="string")

class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    institution: str
    student_id: str = Field(alias="studentId") # Map to camelCase for client if needed
    is_active: bool = False # Will be true after email verification
    is_admin: bool = False
    registered_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True # Allow mapping by alias
        json_encoders = {ObjectId: str} # Convert ObjectId to string for JSON output
        arbitrary_types_allowed = True # Allow custom types like PyObjectId

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserInDB(UserBase):
    id: PyObjectId = Field(alias="_id") # Map MongoDB's _id to 'id'
    hashed_password: str

class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")
