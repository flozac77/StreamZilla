import pytest
from unittest.mock import patch, AsyncMock, MagicMock
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

@pytest.mark.asyncio
async def test_get_game_by_name():
    """Test retrieving a game by name."""
    twitch_service = TwitchService()
    
    # Create a simple mock for httpx.AsyncClient.get
    get_response = MagicMock()
    get_response.json.return_value = {"data": [mock_game_data]}
    
    # Patch the get method and repository save_game method
    with patch("httpx.AsyncClient.get", return_value=get_response), \
         patch.object(twitch_service.repository, "save_game", return_value=None):
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
async def test_search_videos_by_game():
    """Test searching for videos by game name."""
    twitch_service = TwitchService()
    
    # Create a game object for the return value of get_game_by_name
    game = TwitchGame(**mock_game_data)
    
    # Create video objects for the return value of get_videos_by_game_id
    videos = [TwitchVideo(**mock_videos_data[0])]
    
    # Patch all the methods used by search_videos_by_game
    with patch.object(twitch_service.repository, "get_cached_game_search", return_value=None), \
         patch.object(twitch_service, "get_game_by_name", return_value=game), \
         patch.object(twitch_service, "get_videos_by_game_id", return_value=videos), \
         patch.object(twitch_service.repository, "save_game_search_results", return_value=None):
        
        result = await twitch_service.search_videos_by_game("Test Game", "test_token")
    
    # Verify that the result is correct
    assert isinstance(result, TwitchSearchResult)
    assert result.game.id == "67890"
    assert result.game.name == "Test Game"
    assert len(result.videos) == 1
    assert result.videos[0].id == "123456789"
    assert result.videos[0].title == "Test Video"

@pytest.mark.asyncio
async def test_search_videos_by_game_with_cache():
    """Test searching for videos with a cache hit."""
    twitch_service = TwitchService()
    
    # Create a mock cached result
    cached_result = TwitchSearchResult(
        game=TwitchGame(**mock_game_data),
        videos=[TwitchVideo(**mock_videos_data[0])],
        last_updated=datetime.utcnow().isoformat()
    )
    
    # Patch the repository cache method to return our cached result
    with patch.object(twitch_service.repository, "get_cached_game_search", return_value=cached_result):
        result = await twitch_service.search_videos_by_game("Test Game", "test_token")
    
    # Verify that the result is the cached result
    assert isinstance(result, TwitchSearchResult)
    assert result.game.id == "67890"
    assert result.game.name == "Test Game"
    assert len(result.videos) == 1
    assert result.videos[0].id == "123456789"

@pytest.mark.asyncio
async def test_search_videos_by_game_not_found():
    """Test searching for videos when the game is not found."""
    twitch_service = TwitchService()
    
    # Patch methods to simulate game not found
    with patch.object(twitch_service.repository, "get_cached_game_search", return_value=None), \
         patch.object(twitch_service, "get_game_by_name", return_value=None):
        
        result = await twitch_service.search_videos_by_game("Nonexistent Game", "test_token")
    
    # Verify that the result has an empty game and videos
    assert isinstance(result, TwitchSearchResult)
    assert result.game.id == "0"
    assert result.game.name == "Nonexistent Game"
    assert len(result.videos) == 0 