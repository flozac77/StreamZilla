import pytest
from backend.app.config import settings

def test_config_loaded():
    """Test that the configuration is loaded properly."""
    assert settings.TWITCH_CLIENT_ID is not None
    assert settings.TWITCH_CLIENT_SECRET is not None
    assert settings.TWITCH_REDIRECT_URI is not None
    assert settings.MONGODB_URL is not None
    assert settings.MONGODB_DB_NAME is not None
    assert settings.REDIS_URL is not None
    assert settings.SESSION_SECRET_KEY is not None
    assert settings.ENVIRONMENT in ["dev", "test", "prod"]
    # Vérifier d'autres paramètres si nécessaire 