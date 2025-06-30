import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_DETAILS: str = "mongodb+srv://peaceoloruntoba22:181EKRClwi4yKVIw@paymentclust.5j4xnrw.mongodb.net/?retryWrites=true&w=majority&appName=paymentclust"
    DATABASE_NAME: str = "paymentclust"
    JWT_SECRET_KEY: str = "campuspay"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BREVO_API_KEY: str
    EMAIL_FROM_NAME: str = "CampusPay E-Wallet Team"
    EMAIL_FROM_EMAIL: str = "noreply@campuspay.com"
    FRONTEND_BASE_URL: str = "http://localhost:3000" # Default for local frontend development

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
