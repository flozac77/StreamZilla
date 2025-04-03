import pytest
from unittest.mock import patch, AsyncMock, MagicMock, Mock
from backend.app.services.twitch_service import TwitchService
from backend.app.models.twitch import TwitchUser, TwitchToken, TwitchGame, TwitchVideo, TwitchSearchResult
from datetime import datetime

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

mock_game_data = {
    "id": "67890",
    "name": "Test Game",
    "box_art_url": "https://example.com/game.jpg"
}

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

@pytest.fixture
def twitch_service():
    """Create a TwitchService instance for testing"""
    service = TwitchService()
    return service

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
async def test_get_user_info(twitch_service):
    """Test la récupération des informations d'un utilisateur"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [{
            "id": "12345",
            "login": "test_user",
            "display_name": "Test User",
            "type": "user",
            "broadcaster_type": "partner",
            "description": "Test description",
            "profile_image_url": "https://example.com/image.jpg",
            "offline_image_url": "https://example.com/offline.jpg",
            "view_count": 1000,
            "email": "test@example.com",
            "created_at": "2023-01-01T00:00:00Z"
        }]
    }
    mock_response.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        user_info = await twitch_service.get_user_info("test_token")
        assert isinstance(user_info, TwitchUser)
        assert user_info.id == "12345"
        assert user_info.login == "test_user"
        assert user_info.display_name == "Test User"
        assert user_info.type == "user"
        assert user_info.broadcaster_type == "partner"
        assert user_info.description == "Test description"
        assert user_info.profile_image_url == "https://example.com/image.jpg"
        assert user_info.offline_image_url == "https://example.com/offline.jpg"
        assert user_info.view_count == 1000
        assert user_info.email == "test@example.com"
        assert isinstance(user_info.created_at, datetime)

@pytest.mark.asyncio
async def test_get_user_videos(twitch_service):
    """Test la récupération des vidéos d'un utilisateur"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [{
            "id": "123456789",
            "user_id": "987654321",
            "user_login": "testuser",
            "user_name": "Test User",
            "title": "Test Video",
            "description": "Test Description",
            "created_at": "2024-03-25T08:00:00Z",
            "published_at": "2024-03-25T08:00:00Z",
            "url": "https://twitch.tv/videos/123456789",
            "thumbnail_url": "https://test.com/thumb.jpg",
            "viewable": "public",
            "view_count": 100,
            "language": "en",
            "type": "archive",
            "duration": "1h2m3s"
        }]
    }
    mock_response.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        videos = await twitch_service.get_user_videos("987654321", "test_token")
        assert len(videos) == 1
        assert isinstance(videos[0], TwitchVideo)
        assert videos[0].id == "123456789"
        assert videos[0].user_id == "987654321"

@pytest.mark.asyncio
async def test_get_stream_key(twitch_service):
    """Test la récupération de la clé de stream"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [{
            "stream_key": "test-stream-key"
        }]
    }
    mock_response.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        stream_key = await twitch_service.get_stream_key("987654321", "test_token")
        assert stream_key == "test-stream-key"

@pytest.mark.asyncio
async def test_get_game_by_name():
    """Test retrieving a game by name."""
    twitch_service = TwitchService()
    
    # Create a simple mock for httpx.AsyncClient.get
    get_response = MagicMock()
    get_response.json.return_value = {"data": [mock_game_data]}
    
    # Patch the get method
    with patch("httpx.AsyncClient.get", return_value=get_response):
        game = await twitch_service.get_game_by_name("Test Game", "test_token")
    
    # Verify that the result is correct
    assert isinstance(game, TwitchGame)
    assert game.id == "67890"
    assert game.name == "Test Game"
    assert game.box_art_url == "https://example.com/game.jpg"

@pytest.mark.asyncio
async def test_get_game_by_name_not_found():
    """Test retrieving a game that doesn't exist."""
    twitch_service = TwitchService()
    
    # Create a simple mock for httpx.AsyncClient.get
    get_response = MagicMock()
    get_response.json.return_value = {"data": []}
    
    # Patch the get method
    with patch("httpx.AsyncClient.get", return_value=get_response):
        game = await twitch_service.get_game_by_name("Nonexistent Game", "test_token")
    
    # Verify that the result is None for not found
    assert game is None

@pytest.mark.asyncio
async def test_get_videos_by_game_id():
    """Test retrieving videos for a specific game ID."""
    twitch_service = TwitchService()
    
    # Create a simple mock for httpx.AsyncClient.get
    get_response = MagicMock()
    get_response.json.return_value = {"data": mock_videos_data}
    
    # Patch the get method
    with patch("httpx.AsyncClient.get", return_value=get_response):
        videos = await twitch_service.get_videos_by_game_id("67890", "test_token")
    
    # Verify that the result is correct
    assert isinstance(videos, list)
    assert len(videos) == 1
    assert isinstance(videos[0], TwitchVideo)
    assert videos[0].id == "123456789"
    assert videos[0].title == "Test Video"

@pytest.mark.asyncio
async def test_search_videos_by_game(twitch_service):
    """Test la recherche de vidéos par jeu"""
    mock_game_response = Mock()
    mock_game_response.json.return_value = {
        "data": [{
            "id": "123",
            "name": "Test Game",
            "box_art_url": "https://test.com/boxart.jpg"
        }]
    }
    mock_game_response.raise_for_status = Mock()

    mock_videos_response = Mock()
    mock_videos_response.json.return_value = {
        "data": [{
            "id": "123456789",
            "user_id": "987654321",
            "user_login": "testuser",
            "user_name": "Test User",
            "title": "Test Video",
            "description": "Test Description",
            "created_at": "2024-03-25T08:00:00Z",
            "published_at": "2024-03-25T08:00:00Z",
            "url": "https://twitch.tv/videos/123456789",
            "thumbnail_url": "https://test.com/thumb.jpg",
            "viewable": "public",
            "view_count": 100,
            "language": "en",
            "type": "archive",
            "duration": "1h2m3s"
        }]
    }
    mock_videos_response.raise_for_status = Mock()

    # Mock du token repository et du auth service
    token_data = TwitchToken(**mock_token)
    mock_token_repository = AsyncMock()
    mock_token_repository.get_current_token.return_value = token_data
    mock_auth_service = AsyncMock()
    mock_auth_service.get_valid_token.return_value = token_data

    with patch("httpx.AsyncClient.get", side_effect=[mock_game_response, mock_videos_response]), \
         patch("backend.app.services.twitch_service.TwitchAuthService", return_value=mock_auth_service), \
         patch("backend.app.services.twitch_service.TokenRepository", return_value=mock_token_repository):
        result = await twitch_service.search_videos_by_game("Test Game")
        assert isinstance(result, TwitchSearchResult)
        assert isinstance(result.game, TwitchGame)
        assert result.game.name == "Test Game"
        assert len(result.videos) == 1
        assert isinstance(result.videos[0], TwitchVideo)
        assert result.videos[0].id == "123456789"
        assert isinstance(result.last_updated, datetime)

@pytest.mark.asyncio
async def test_search_videos_by_game_with_cache():
    """Test searching for videos with a cache hit."""
    twitch_service = TwitchService()
    
    # Mock des réponses API
    mock_game_response = Mock()
    mock_game_response.json.return_value = {"data": [mock_game_data]}
    mock_game_response.raise_for_status = Mock()

    mock_videos_response = Mock()
    mock_videos_response.json.return_value = {"data": mock_videos_data}
    mock_videos_response.raise_for_status = Mock()

    # Mock du token repository et du auth service
    token_data = TwitchToken(**mock_token)
    mock_token_repository = AsyncMock()
    mock_token_repository.get_current_token.return_value = token_data
    mock_auth_service = AsyncMock()
    mock_auth_service.get_valid_token.return_value = token_data

    with patch("httpx.AsyncClient.get", side_effect=[mock_game_response, mock_videos_response]), \
         patch("backend.app.services.twitch_service.TwitchAuthService", return_value=mock_auth_service), \
         patch("backend.app.services.twitch_service.TokenRepository", return_value=mock_token_repository):
        result = await twitch_service.search_videos_by_game("Test Game")
    
    # Verify that the result is correct
    assert isinstance(result, TwitchSearchResult)
    assert result.game.id == "67890"
    assert result.game.name == "Test Game"
    assert len(result.videos) == 1
    assert result.videos[0].id == "123456789"

@pytest.mark.asyncio
async def test_search_videos_by_game_not_found(twitch_service):
    """Test la recherche de vidéos pour un jeu qui n'existe pas"""
    mock_response = Mock()
    mock_response.json.return_value = {"data": []}
    mock_response.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await twitch_service.search_videos_by_game("Nonexistent Game", "test_token")
        assert isinstance(result, TwitchSearchResult)
        assert result.game is None
        assert len(result.videos) == 0
        assert isinstance(result.last_updated, datetime) 