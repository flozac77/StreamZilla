import pytest
from backend.app.config import settings, DevSettings, TestSettings, ProdSettings
from unittest.mock import patch, MagicMock
import os
from pydantic import ValidationError

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

@pytest.mark.asyncio
async def test_settings_initialization():
    """Test l'initialisation des settings avec des variables d'environnement."""
    env_vars = {
        "TWITCH_CLIENT_ID": "test_client_id",
        "TWITCH_CLIENT_SECRET": "test_client_secret",
        "TWITCH_REDIRECT_URI": "http://test.com/callback",
        "MONGODB_URL": "mongodb://test:27017",
        "MONGODB_DB_NAME": "test_db",
        "REDIS_URL": "redis://test:6379",
        "SESSION_SECRET_KEY": "test_secret",
        "ENVIRONMENT": "dev"
    }
    
    with patch.dict(os.environ, env_vars):
        # Créer une nouvelle instance de DevSettings
        test_settings = DevSettings()
        
        # Vérifier les valeurs
        assert test_settings.TWITCH_CLIENT_ID == "test_client_id"
        assert test_settings.TWITCH_CLIENT_SECRET == "test_client_secret"
        assert test_settings.TWITCH_REDIRECT_URI == "http://test.com/callback"
        assert test_settings.MONGODB_URL == "mongodb://test:27017"
        assert test_settings.MONGODB_DB_NAME == "test_db"
        assert test_settings.REDIS_URL == "redis://test:6379"
        assert test_settings.SESSION_SECRET_KEY == "test_secret"
        assert test_settings.ENVIRONMENT == "dev"

def test_settings_missing_env():
    """Test que les valeurs par défaut sont utilisées quand les variables d'environnement sont manquantes"""
    os.environ.clear()
    
    # Vérifier que les valeurs par défaut de l'environnement dev sont utilisées
    dev_settings = DevSettings()
    assert dev_settings.ENVIRONMENT == "dev"
    assert dev_settings.TWITCH_REDIRECT_URI == "https://dd9e-2001-861-49c3-9eb0-4ce7-58da-632d-8062.ngrok-free.app/callback"
    assert dev_settings.MONGODB_URL == "mongodb://localhost:27017"
    assert dev_settings.MONGODB_DB_NAME == "dbTwitch"
    assert dev_settings.REDIS_URL == "redis://localhost:6379"
    assert dev_settings.CACHE_TTL == 3600
    assert dev_settings.CACHE_MAX_SIZE == 1000
    
    # Test de la validation des champs requis
    with pytest.raises(ValidationError) as exc_info:
        DevSettings(TWITCH_CLIENT_ID=None, TWITCH_CLIENT_SECRET=None)
    assert "TWITCH_CLIENT_ID" in str(exc_info.value)
    assert "TWITCH_CLIENT_SECRET" in str(exc_info.value)

def test_settings_instance():
    """Test que les paramètres sont correctement chargés"""
    os.environ["TWITCH_CLIENT_ID"] = "test_client_id"
    os.environ["TWITCH_CLIENT_SECRET"] = "test_client_secret"
    os.environ["TWITCH_REDIRECT_URI"] = "http://localhost:3000/callback"
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
    os.environ["MONGODB_DB_NAME"] = "test_db"
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    os.environ["SESSION_SECRET_KEY"] = "test_secret_key"
    os.environ["ENVIRONMENT"] = "test"

    test_settings = TestSettings()
    assert test_settings.TWITCH_CLIENT_ID == "test_client_id"
    assert test_settings.TWITCH_CLIENT_SECRET == "test_client_secret"
    assert test_settings.TWITCH_REDIRECT_URI == "http://localhost:3000/callback"
    assert test_settings.MONGODB_URL == "mongodb://localhost:27017"
    assert test_settings.MONGODB_DB_NAME == "test_db"
    assert test_settings.REDIS_URL == "redis://localhost:6379"
    assert test_settings.SESSION_SECRET_KEY == "test_secret_key"
    assert test_settings.ENVIRONMENT == "test" 