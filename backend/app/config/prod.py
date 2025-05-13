from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import secrets

class ProdSettings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "prod"
    
    # Twitch API settings
    TWITCH_CLIENT_ID: str
    TWITCH_CLIENT_SECRET: str
    TWITCH_REDIRECT_URI: str
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb+srv://flozac:uT8H8pVQeoJS3LXW@clustermogodb.kqbsqxc.mongodb.net/?retryWrites=true&w=majority"
    MONGODB_DB_NAME: str = "dbTwitch"
    
    # Redis settings
    REDIS_URL: str
    
    # Session settings
    SESSION_SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 1000
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True) 