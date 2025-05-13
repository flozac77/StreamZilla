from .dev import DevSettings
from .prod import ProdSettings
from .test import TestSettings
import os

def get_settings():
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "prod")
    if env == "prod":
        return ProdSettings()
    elif env == "test":
        return TestSettings()
    return DevSettings()

# Get environment from environment variable or default to development
ENV = os.getenv("ENVIRONMENT", "prod")

# Get settings based on environment
settings = get_settings()

# Debug print
print(f"Current environment: {ENV}")
print(f"TWITCH_REDIRECT_URI: {settings.TWITCH_REDIRECT_URI}")
print(f"TWITCH_CLIENT_ID: {settings.TWITCH_CLIENT_ID}")
print(f"MONGODB_URL: {settings.MONGODB_URL}")
print(f"MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")
print(f"REDIS_URL: {settings.REDIS_URL}")

__all__ = ["settings", "get_settings"] 