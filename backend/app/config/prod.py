from backend.app.config.base import Settings # Importer depuis le nouveau fichier base.py
from typing import List
import secrets
import os

class ProdSettings(Settings): # Inherit from base Settings
    # Environment
    ENVIRONMENT: str = "prod"
    DEBUG: bool = False # DEBUG must be False in production
    LOG_LEVEL: str = "INFO" # Standard production log level
    
    # Twitch API settings
    # These will be loaded from .env via Settings, or environment variables.
    # Ensure these are set in the production environment.
    # TWITCH_CLIENT_ID: str
    # TWITCH_CLIENT_SECRET: str
    # TWITCH_REDIRECT_URI: str
    
    # MongoDB settings
    # MONGODB_URL: str # Loaded from .env via Settings
    # MONGODB_DB_NAME: str = "dbTwitch" # Can be inherited or overridden
    
    # Redis settings
    # REDIS_URL: str # Loaded from .env via Settings
    
    # Session settings
    # SESSION_SECRET_KEY: str # Loaded from .env via Settings, should be strong
    # Fallback to a new secret if not in .env, though .env is preferred for prod.
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))

    # Cache settings - can be inherited or overridden
    # CACHE_TTL: int = 3600
    # CACHE_MAX_SIZE: int = 1000

    # API_URL - should be the production API URL, loaded from .env via Settings
    # API_URL: str = os.getenv("API_URL", "http://localhost:8000") # Example
    # FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173") # Example
