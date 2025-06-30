# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId

from pydantic_core import CoreSchema # This might still be needed for complex validators
from pydantic.json_schema import JsonSchemaValue # Use this for schema modification


class PyObjectId(ObjectId):
    """Custom Type for MongoDB ObjectId to work with Pydantic v2."""

    @classmethod
    def __get_validators__(cls):
        # This part is mostly for Pydantic v1 backward compatibility,
        # but is still good to keep for direct validation.
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId or string representation")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: JsonSchemaValue
    ) -> JsonSchemaValue:
        # Here we modify the JSON schema representation for OpenAPI docs and serialization
        # We tell Pydantic that this should be treated as a string with a specific format.
        return handler(core_schema).copy(
            # Override or add properties for the JSON schema representation
            type="string",
            format="objectid", # Custom format for OpenAPI documentation
            examples=["60c72b2f9b1d8c0d1e3a4b5c"], # Example for documentation
        )


# Rest of your user.py file remains the same
# ...
class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    institution: str
    student_id: str = Field(alias="studentId")
    is_active: bool = False
    is_admin: bool = False
    registered_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        # For Pydantic V2, json_encoders is generally handled by __get_pydantic_json_schema__
        # or by directly setting it in the model_config or custom serializers.
        # However, keeping it here for ObjectId: str might still work as a fallback for direct dumps.
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True # Keep this if you have complex types Pydantic doesn't natively handle

        # Pydantic V2 equivalent for Config if needed:
        # model_config = ConfigDict(
        #     populate_by_name=True,
        #     json_encoders={ObjectId: str}, # This is for model.json() / model.model_dump_json()
        #     arbitrary_types_allowed=True,
        # )

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserInDB(UserBase):
    id: PyObjectId = Field(alias="_id") # Map MongoDB's _id to 'id'
    hashed_password: str

class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")