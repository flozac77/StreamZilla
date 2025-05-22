from backend.app.config.base import Settings # Importer depuis le nouveau fichier base.py
from typing import List
import secrets

class TestSettings(Settings): # Inherit from base Settings
    # Environment
    ENVIRONMENT: str = "test"
    DEBUG: bool = True # Typically true for tests to get more info
    LOG_LEVEL: str = "DEBUG" # Or "INFO" if too verbose
    
    # Twitch API settings - Test-specific values
    TWITCH_CLIENT_ID: str = "test_client_id"
    TWITCH_CLIENT_SECRET: str = "test_client_secret"
    TWITCH_REDIRECT_URI: str = "http://localhost:8000/callback" # Default, might be overridden by .env
    
    # MongoDB settings - Test-specific database name
    # MONGODB_URL: str # Inherited, expect from .env or default "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dbTwitchTest" # Specific for testing
    
    # Redis settings - Inherited, expect from .env or default "redis://localhost:6379"
    # REDIS_URL: str = "redis://localhost:6379"
    
    # Session settings - Test-specific key
    SESSION_SECRET_KEY: str = "test-secret-key" # Fixed key for tests
    
    # Cache settings - Test-specific values, e.g., shorter TTL
    CACHE_TTL: int = 60  # 1 minute, override for tests
    CACHE_MAX_SIZE: int = 10 # Smaller cache for tests

    # API_URL - can be inherited or overridden if test server is different
    # API_URL: str = "http://localhost:8000" 

