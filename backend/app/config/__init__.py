from .dev import DevSettings
from .prod import ProdSettings
from .test import TestSettings
import os
import logging

logger = logging.getLogger(__name__)

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

# Safe startup logging (no secrets)
logger.info(f"Environment: {ENV}")

__all__ = ["settings", "get_settings"] 