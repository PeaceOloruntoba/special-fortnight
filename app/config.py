import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_DETAILS: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "e_wallet_db"
    JWT_SECRET_KEY: str = "ewallet_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BREVO_API_KEY: str
    EMAIL_FROM_NAME: str = "CampusPay E-Wallet Team"
    EMAIL_FROM_EMAIL: str = "dev@campuspay.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()