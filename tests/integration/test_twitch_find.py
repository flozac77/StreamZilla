import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.main import app
from datetime import datetime

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_twitch_game_response():
    """Provides a mock response from Twitch API for a game."""
    return {
        "data": [
            {
                "id": "12345",
                "name": "Test Game",
                "box_art_url": "https://example.com/game.jpg"
            }
        ]
    }

@pytest.fixture
def mock_twitch_videos_response():
    """Provides a mock response from Twitch API for videos."""
    return {
        "data": [
            {
                "id": "123456789",
                "user_id": "54321",
                "user_login": "test_user",
                "user_name": "Test User",
                "title": "Test Video 1",
                "description": "A test video",
                "created_at": "2023-01-01T00:00:00Z",
                "published_at": "2023-01-01T00:00:00Z",
                "url": "https://twitch.tv/videos/123456789",
                "thumbnail_url": "https://example.com/thumbnail1.jpg",
                "viewable": "public",
                "view_count": 100,
                "language": "en",
                "type": "archive",
                "duration": "1h30m"
            },
            {
                "id": "987654321",
                "user_id": "54321",
                "user_login": "test_user2",
                "user_name": "Test User 2",
                "title": "Test Video 2",
                "description": "Another test video",
                "created_at": "2023-01-02T00:00:00Z",
                "published_at": "2023-01-02T00:00:00Z",
                "url": "https://twitch.tv/videos/987654321",
                "thumbnail_url": "https://example.com/thumbnail2.jpg",
                "viewable": "public",
                "view_count": 200,
                "language": "en",
                "type": "archive",
                "duration": "2h45m"
            }
        ]
    }

def test_search_videos_success(test_client, mock_twitch_game_response, mock_twitch_videos_response):
    """
    Test that the /api/twitch/search endpoint correctly finds videos
    for a game when the Twitch API calls succeed.
    """
    # Configuration des mocks pour simuler les réponses de l'API Twitch
    with patch('httpx.AsyncClient.get') as mock_get, \
         patch('backend.app.repositories.twitch_repository.TwitchRepository.get_cached_game_search') as mock_cache:
        
        # Ensure the cache is not used
        mock_cache.return_value = None
        
        # Setup responses for the two API calls
        # First call for game search
        # Second call for videos
        mock_get.side_effect = [
            MagicMock(json=MagicMock(return_value=mock_twitch_game_response)),
            MagicMock(json=MagicMock(return_value=mock_twitch_videos_response))
        ]

        # Call the endpoint with cache disabled
        response = test_client.get(
            "/api/twitch/search?game_name=Test Game&use_cache=false", 
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        
        # Verify the structure and content of the data
        assert "game" in data
        assert "videos" in data
        assert "last_updated" in data
        
        # Check game data
        assert data["game"]["id"] == "12345"
        assert data["game"]["name"] == "Test Game"
        assert data["game"]["box_art_url"] == "https://example.com/game.jpg"
        
        # Check videos data
        assert len(data["videos"]) == 2
        assert data["videos"][0]["id"] == "123456789"
        assert data["videos"][0]["title"] == "Test Video 1"
        assert data["videos"][1]["id"] == "987654321"
        assert data["videos"][1]["title"] == "Test Video 2"

def test_search_videos_game_not_found(test_client):
    """
    Test that the /api/twitch/search endpoint correctly handles the case
    where the game is not found.
    """
    # Configure the mock to simulate an empty response from the Twitch API
    with patch('httpx.AsyncClient.get') as mock_get:
        empty_response = MagicMock()
        empty_response.json.return_value = {"data": []}
        mock_get.return_value = empty_response

        # Call the endpoint
        response = test_client.get(
            "/api/twitch/search?game_name=nonexistent_game", 
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response - should return 200 with empty results
        assert response.status_code == 200
        data = response.json()
        
        # Check for empty game with default values
        assert data["game"]["id"] == "0"
        assert data["game"]["name"] == "nonexistent_game"
        assert data["game"]["box_art_url"] == ""
        
        # Check for empty videos list
        assert len(data["videos"]) == 0 