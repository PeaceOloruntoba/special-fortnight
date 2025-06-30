from pydantic import BaseModel, EmailStr, Field
from typing import Any, Optional
from datetime import datetime
from bson import ObjectId
from pydantic_core import CoreSchema, PydanticCustomType  # For handling MongoDB's _id

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    # --- START OF PYDANTIC V2 CHANGE ---
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> CoreSchema:
        return PydanticCustomType.new_schema(
            cls.validate, # The validator function
            json_schema={
                "type": "string",
                "pattern": "^[0-9a-fA-F]{24}$", # Optional: add a pattern for ObjectID format
            },
        )
    # --- END OF PYDANTIC V2 CHANGE ---

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
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserInDB(UserBase):
    id: PyObjectId = Field(alias="_id") # Map MongoDB's _id to 'id'
    hashed_password: str

class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")
    
    


    id: PyObjectId = Field(alias="_id")