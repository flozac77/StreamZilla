from backend.app.config.base import Settings # Importer depuis le nouveau fichier base.py

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
    # SESSION_SECRET_KEY is required from .env in production
    # Do NOT fallback to secrets.token_urlsafe() - it will regenerate on each deploy

    # Cache settings - can be inherited or overridden
    # CACHE_TTL: int = 3600
    # CACHE_MAX_SIZE: int = 1000

    # API_URL - should be the production API URL, loaded from .env via Settings
    # API_URL: str = os.getenv("API_URL", "http://localhost:8000") # Example

    # FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173") # Example

    # CORS settings
    # Production: set ALLOWED_ORIGINS in .env to comma-separated list
    # Example: ALLOWED_ORIGINS='["https://yourdomain.com","https://app.yourdomain.com"]'
    ALLOWED_ORIGINS: list[str] = []  # Prod must explicitly set origins in .env

