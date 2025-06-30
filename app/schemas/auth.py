# app/schemas/auth.py
from pydantic import BaseModel
from typing import Optional # Ensure this is imported if you're using Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel): # <--- THIS IS THE CLASS IN QUESTION
    email: str | None = None # Changed from username to email for MongoDB setup