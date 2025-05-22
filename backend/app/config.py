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
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379")
    
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

@lru_cache()
def get_settings() -> Settings:
    """Get the appropriate settings based on the environment."""
    env = os.getenv("ENVIRONMENT", "dev") # Read ENVIRONMENT, default to "dev"
    if env == "dev":
        from backend.app.config.dev import DevSettings as AppDevSettings
        return AppDevSettings()
    elif env == "test":
        from backend.app.config.test import TestSettings as AppTestSettings
        return AppTestSettings()
    elif env == "prod":
        from backend.app.config.prod import ProdSettings as AppProdSettings
        return AppProdSettings()
    return Settings() # Fallback to base settings

settings = get_settings()
