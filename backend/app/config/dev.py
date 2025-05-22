from backend.app.config.base import Settings  # Importer depuis le nouveau fichier base.py
from typing import List
import secrets

class DevSettings(Settings):  # Inherit from base Settings
    # Environment
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True # Add DEBUG specific to dev
    LOG_LEVEL: str = "DEBUG" # Add LOG_LEVEL specific to dev
    
    # Twitch API settings
    # These will override Settings if set in .env or here
    # TWITCH_CLIENT_ID: str  # Already in base, loaded from .env
    # TWITCH_CLIENT_SECRET: str # Already in base, loaded from .env
    # ngrok uniquement pour le callback Twitch - Specific dev override
    TWITCH_REDIRECT_URI: str = "https://dd9e-2001-861-49c3-9eb0-4ce7-58da-632d-8062.ngrok-free.app/callback"
    
    # MongoDB settings - Specific dev overrides or defaults
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dbTwitch"
    
    # Redis settings - Specific dev override or default
    REDIS_URL: str = "redis://localhost:6379"
    
    # Session settings - Specific dev override
    SESSION_SECRET_KEY: str = "dev-secret-key" # Override with a fixed dev key
    
    # API_URL - Specific dev override
    API_URL: str = "http://localhost:8000"

    # Cache settings will be inherited from Settings unless overridden here
    # CACHE_TTL: int = 3600
    # CACHE_MAX_SIZE: int = 1000
  