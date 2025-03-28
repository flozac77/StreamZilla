import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Configuration settings for the application."""
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    TWITCH_CLIENT_ID: str
    TWITCH_CLIENT_SECRET: str
    TWITCH_REDIRECT_URI: str
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "visibrain"
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_SECRET_KEY: str = "your-secret-key-here"  # À remplacer en production
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 100
    RATE_LIMIT_CALLS: int = 30
    RATE_LIMIT_PERIOD: int = 60  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

class DevSettings(Settings):
    """Development settings."""
    ENVIRONMENT: str = "dev"
    TWITCH_CLIENT_ID: str 
    TWITCH_CLIENT_SECRET: str 
    # ngrok uniquement pour le callback Twitch
    TWITCH_REDIRECT_URI: str = "https://dd9e-2001-861-49c3-9eb0-4ce7-58da-632d-8062.ngrok-free.app/callback"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "visibrain"
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_SECRET_KEY: str = "dev-secret-key"
    API_URL: str = "http://localhost:8000"  # URL locale pour l'API

class TestSettings(Settings):
    """Test settings."""
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
    env = os.getenv("ENV", "dev")
    settings_map = {
        "dev": DevSettings,
        "test": TestSettings,
        "prod": ProdSettings,
    }
    settings_class = settings_map.get(env, DevSettings)
    settings = settings_class()
    print(f"Current environment: {settings.ENVIRONMENT}")
    print(f"TWITCH_REDIRECT_URI: {settings.TWITCH_REDIRECT_URI}")
    print(f"TWITCH_CLIENT_ID: {settings.TWITCH_CLIENT_ID}")
    print(f"MONGODB_URL: {settings.MONGODB_URL}")
    print(f"MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")
    print(f"REDIS_URL: {settings.REDIS_URL}")
    return settings

settings = get_settings()
