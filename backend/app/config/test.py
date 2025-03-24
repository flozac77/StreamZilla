from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import secrets

class TestSettings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "test"
    
    # Twitch API settings
    TWITCH_CLIENT_ID: str = "test_client_id"
    TWITCH_CLIENT_SECRET: str = "test_client_secret"
    TWITCH_REDIRECT_URI: str = "http://localhost:8000/callback"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dbTwitch_test"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Session settings
    SESSION_SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Cache settings
    CACHE_TTL: int = 60  # 1 minute
    CACHE_MAX_SIZE: int = 100
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True) 