import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.services.twitch.auth import TwitchAuthService
from backend.app.repositories.token_repository import TokenRepository
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app
from backend.config import settings

@pytest.fixture
async def test_db():
    """Create a test database and clean it up after the test."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.dbTwitch_test
    yield db
    await client.drop_database("dbTwitch_test")

@pytest.fixture
async def token_repository(test_db):
    repo = TokenRepository(test_db)
    await repo.initialize()
    return repo

@pytest.fixture
async def auth_service(token_repository):
    service = TwitchAuthService(token_repository)
    yield service
    await service.close()

client = TestClient(app)

def test_auth_test_endpoint():
    """Test l'endpoint de test d'authentification"""
    response = client.get("/api/auth/test")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert isinstance(data["status"], bool)

@patch('backend.app.services.twitch.auth.TwitchAuthService.validate_token')
def test_auth_test_with_valid_token(mock_validate):
    """Test l'authentification avec un token valide"""
    mock_validate.return_value = True
    response = client.get("/api/auth/test")
    assert response.status_code == 200
    assert response.json() == {"status": True}

@patch('backend.app.services.twitch.auth.TwitchAuthService.validate_token')
def test_auth_test_with_invalid_token(mock_validate):
    """Test l'authentification avec un token invalide"""
    mock_validate.return_value = False
    response = client.get("/api/auth/test")
    assert response.status_code == 200
    assert response.json() == {"status": False}

@pytest.mark.asyncio
async def test_generate_token(auth_service):
    """Test la génération d'un token valide"""
    token = await auth_service.get_valid_token()
    assert token is not None
    assert token.access_token is not None
    assert token.is_valid is True

@pytest.mark.asyncio
async def test_token_validation(auth_service):
    token = await auth_service.get_valid_token()
    is_valid = await auth_service._is_token_valid(token)
    assert is_valid is True

@patch('backend.app.services.twitch.auth.TwitchAuthService.get_oauth_url')
def test_auth_url_endpoint(mock_get_url):
    """Test l'endpoint qui retourne l'URL d'authentification"""
    expected_url = "https://id.twitch.tv/oauth2/authorize?..."
    mock_get_url.return_value = expected_url
    
    response = client.get("/api/twitch/auth/url")
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == expected_url 