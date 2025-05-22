from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import secrets

class Settings(BaseSettings):
    # Définir ici tous les paramètres de configuration communs à tous les environnements
    # et ceux qui sont chargés depuis le fichier .env

    # Twitch API settings
    TWITCH_CLIENT_ID: str
    TWITCH_CLIENT_SECRET: str
    # TWITCH_REDIRECT_URI: str # Peut être défini dans les classes spécifiques si différent

    # MongoDB settings
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "dbTwitch" # Default value

    # Redis settings
    REDIS_URL: str

    # Session settings
    SESSION_SECRET_KEY: str = secrets.token_urlsafe(32) # Default with a random key

    # Cache settings
    CACHE_TTL: int = 3600 # 1 hour default
    CACHE_MAX_SIZE: int = 1000 # Default max size

    # API_URL - Base URL of your backend API
    API_URL: str = "http://localhost:8000" # Default value

    # Frontend URL (useful for CORS or redirects)
    FRONTEND_URL: str = "http://localhost:5173" # Default value

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore") 