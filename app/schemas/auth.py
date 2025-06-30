from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr | None = None # Changed from username to email for MongoDB setup

# --- NEW SCHEMAS FOR PASSWORD RESET ---
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str # The reset token received via email
    new_password: str
    confirm_new_password: str