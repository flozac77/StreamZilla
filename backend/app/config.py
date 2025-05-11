import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Configuration settings for the application."""
    PROJECT_NAME: str = "VisioBrain API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENV", "dev")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API URLs
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Twitch
    TWITCH_CLIENT_ID: str = os.getenv("TWITCH_CLIENT_ID", "")
    TWITCH_CLIENT_SECRET: str = os.getenv("TWITCH_CLIENT_SECRET", "")
    TWITCH_REDIRECT_URI: str = os.getenv("TWITCH_REDIRECT_URI", "")
    
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "dbTwitch")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "your-secret-key-here")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "100"))
    RATE_LIMIT_CALLS: int = int(os.getenv("RATE_LIMIT_CALLS", "30"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

class DevSettings(Settings):
    """Development settings."""
    PROJECT_NAME: str = "VisioBrain API - Dev"
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    TWITCH_CLIENT_ID: str 
    TWITCH_CLIENT_SECRET: str 
    # ngrok uniquement pour le callback Twitch
    TWITCH_REDIRECT_URI: str = "https://dd9e-2001-861-49c3-9eb0-4ce7-58da-632d-8062.ngrok-free.app/callback"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dbTwitch"
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_SECRET_KEY: str = "dev-secret-key"
    API_URL: str = "http://localhost:8000"  # URL locale pour l'API

class TestSettings(Settings):
    """Test settings."""
    PROJECT_NAME: str = "VisioBrain API - Test"
    ENVIRONMENT: str = "test"
    TWITCH_CLIENT_ID: str = "test-client-id"
    TWITCH_CLIENT_SECRET: str = "test-client-secret"
    TWITCH_REDIRECT_URI: str = "http://localhost:8000/callback"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dbTwitchTest"
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_SECRET_KEY: str = "test-secret-key"

class ProdSettings(Settings):
    """Production settings."""
    PROJECT_NAME: str = "VisioBrain API - Production"
    ENVIRONMENT: str = "prod"
    TWITCH_CLIENT_ID: str = os.getenv("TWITCH_CLIENT_ID", "")
    TWITCH_CLIENT_SECRET: str = os.getenv("TWITCH_CLIENT_SECRET", "")
    TWITCH_REDIRECT_URI: str = os.getenv("TWITCH_REDIRECT_URI", "")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "dbTwitch")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "")

@lru_cache()
def get_settings() -> Settings:
    """Get the appropriate settings based on the environment."""
    return Settings()

settings = get_settings()
