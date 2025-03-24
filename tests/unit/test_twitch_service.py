import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.app.services.twitch_service import TwitchService
from backend.app.models.twitch import TwitchUser, TwitchToken

# Définition des données de test
mock_token = {
    "access_token": "test_access_token",
    "refresh_token": "test_refresh_token",
    "expires_in": 3600,
    "token_type": "bearer",
    "scope": ["user:read:email"]
}

mock_user_data = {
    "id": "12345",
    "login": "test_user",
    "display_name": "Test User",
    "profile_image_url": "https://example.com/avatar.jpg",
    "email": "test@example.com"
}

@pytest.fixture
def twitch_service():
    """Create a TwitchService instance for testing"""
    return TwitchService()

@pytest.mark.asyncio
async def test_get_auth_url(twitch_service):
    """Test generation of Twitch authentication URL"""
    auth_url = await twitch_service.get_auth_url()
    assert "id.twitch.tv/oauth2/authorize" in auth_url
    assert "client_id" in auth_url
    assert "redirect_uri" in auth_url

@pytest.mark.asyncio
async def test_exchange_code_for_token():
    """Test exchanging an authorization code for a token."""
    twitch_service = TwitchService()
    
    # Create a simple mock for httpx.AsyncClient.post
    post_response = MagicMock()
    post_response.json.return_value = mock_token
    
    # Patch the post method
    with patch("httpx.AsyncClient.post", return_value=post_response):
        token_data = await twitch_service.exchange_code_for_token("test_code")
    
    # Verify that the result is correct
    assert isinstance(token_data, TwitchToken)
    assert token_data.access_token == "test_access_token"
    assert token_data.token_type == "bearer"

@pytest.mark.asyncio
async def test_get_user_info():
    """Test retrieving Twitch user information."""
    twitch_service = TwitchService()
    
    # Create a simple mock for httpx.AsyncClient.get
    get_response = MagicMock()
    get_response.json.return_value = {"data": [mock_user_data]}
    
    # Patch the get method
    with patch("httpx.AsyncClient.get", return_value=get_response):
        user_info = await twitch_service.get_user_info("test_token")
    
    # Verify that the result is correct
    assert isinstance(user_info, TwitchUser)
    assert user_info.id == "12345"
    assert user_info.display_name == "Test User"

@pytest.mark.asyncio
async def test_get_user_videos():
    """Test retrieving videos for a Twitch user."""
    twitch_service = TwitchService()
    mock_videos_data = [
        {
            "id": "123456789",
            "user_id": "12345",
            "user_login": "test_user",
            "user_name": "Test User",
            "title": "Test Video",
            "description": "A test video",
            "created_at": "2023-01-01T00:00:00Z",
            "published_at": "2023-01-01T00:00:00Z",
            "url": "https://twitch.tv/videos/123456789",
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "viewable": "public",
            "view_count": 100,
            "language": "en",
            "type": "archive",
            "duration": "1h30m"
        }
    ]
    
    # Create a simple mock for httpx.AsyncClient.get
    get_response = MagicMock()
    get_response.json.return_value = {"data": mock_videos_data}
    
    # Patch the get method
    with patch("httpx.AsyncClient.get", return_value=get_response):
        videos = await twitch_service.get_user_videos("12345", "test_token")
    
    # Verify that the result is correct
    assert isinstance(videos, list)
    assert len(videos) == 1
    assert videos[0]["id"] == "123456789"
    assert videos[0]["title"] == "Test Video"

@pytest.mark.asyncio
async def test_get_stream_key():
    """Test retrieving stream key for a Twitch user."""
    twitch_service = TwitchService()
    mock_stream_key_data = [{"stream_key": "test-stream-key"}]
    
    # Create a simple mock for httpx.AsyncClient.get
    get_response = MagicMock()
    get_response.json.return_value = {"data": mock_stream_key_data}
    
    # Patch the get method
    with patch("httpx.AsyncClient.get", return_value=get_response):
        stream_key = await twitch_service.get_stream_key("12345", "test_token")
    
    # Verify that the result is correct
    assert isinstance(stream_key, dict)
    assert "data" in stream_key
    assert stream_key["data"][0]["stream_key"] == "test-stream-key" 