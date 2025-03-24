import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.main import app
from backend.app.models.twitch import TwitchUser, TwitchToken

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_auth_url_endpoint(test_client):
    """Test the /api/twitch/auth/url endpoint"""
    # Configure mocks for HTTP calls
    with patch('backend.app.services.twitch_service.TwitchService.get_auth_url') as mock_get_auth_url:
        mock_get_auth_url.return_value = "https://id.twitch.tv/oauth2/authorize?client_id=test&redirect_uri=test&response_type=code&scope=test"
        
        # Call the endpoint
        response = test_client.get("/api/twitch/auth/url")
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "id.twitch.tv/oauth2/authorize" in data["url"]

def test_callback_endpoint(test_client, mock_twitch_token, mock_twitch_response):
    """Test the /api/twitch/auth/callback endpoint"""
    # Configure the mock for the HTTP call
    with patch('httpx.AsyncClient.post') as mock_post, \
         patch('httpx.AsyncClient.get') as mock_get:
        
        post_response = MagicMock()
        post_response.json.return_value = mock_twitch_token
        mock_post.return_value = post_response
        
        get_response = MagicMock()
        get_response.json.return_value = mock_twitch_response
        mock_get.return_value = get_response
        
        # Call the endpoint
        response = test_client.get("/api/twitch/auth/callback?code=test_code")
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["id"] == "12345"
        assert data["token"]["access_token"] == "test_access_token"

def test_user_info_endpoint(test_client, mock_twitch_response):
    """Test the /api/twitch/user/info endpoint"""
    # Configure the mock for the HTTP call
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = mock_twitch_response
        mock_get.return_value = get_response
        
        # Configure test data
        headers = {"Authorization": "Bearer test_token"}
        
        # Call the endpoint
        response = test_client.get("/api/twitch/user/info", headers=headers)
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "12345"
        assert data["login"] == "test_user"

def test_user_videos_endpoint(test_client):
    """Test the /api/twitch/user/videos endpoint"""
    # Configure the mock for the HTTP call
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_video_data = {
            "data": [
                {
                    "id": "video123",
                    "title": "Test Video",
                    "url": "https://twitch.tv/videos/123"
                }
            ]
        }
        
        get_response = MagicMock()
        get_response.json.return_value = mock_video_data
        mock_get.return_value = get_response
        
        # Configure test data
        headers = {"Authorization": "Bearer test_token"}
        
        # Call the endpoint
        response = test_client.get("/api/twitch/user/videos?user_id=12345", headers=headers)
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["id"] == "video123"
        assert data[0]["title"] == "Test Video"

def test_stream_key_endpoint(test_client):
    """Test the /api/twitch/user/stream-key endpoint"""
    # Configure the mock for the HTTP call
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_stream_key_data = {
            "data": [
                {
                    "stream_key": "test-stream-key"
                }
            ]
        }
        
        get_response = MagicMock()
        get_response.json.return_value = mock_stream_key_data
        mock_get.return_value = get_response
        
        # Configure test data
        headers = {"Authorization": "Bearer test_token"}
        
        # Call the endpoint
        response = test_client.get("/api/twitch/user/stream-key?user_id=12345", headers=headers)
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"][0]["stream_key"] == "test-stream-key"

def test_search_videos_by_game_endpoint(test_client, mock_twitch_game, mock_twitch_videos):
    """Test the /api/twitch/search endpoint for searching videos by game"""
    # Configure the mocks for the HTTP calls
    with patch('httpx.AsyncClient.get') as mock_get, \
         patch('backend.app.repositories.twitch_repository.TwitchRepository.get_cached_game_search') as mock_cache:
        
        # Ensure the cache is not used
        mock_cache.return_value = None
        
        # Setup the responses for the two API calls
        # First call for game search, second call for videos
        mock_get.side_effect = [
            MagicMock(json=MagicMock(return_value=mock_twitch_game)),
            MagicMock(json=MagicMock(return_value=mock_twitch_videos))
        ]
        
        # Configure test data
        headers = {"Authorization": "Bearer test_token"}
        
        # Call the endpoint with cache disabled
        response = test_client.get("/api/twitch/search?game_name=Test%20Game&use_cache=false", headers=headers)
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        
        # Check the structure of the response
        assert "game" in data
        assert "videos" in data
        assert "last_updated" in data
        
        # Check game data
        assert data["game"]["id"] == "12345"
        assert data["game"]["name"] == "Test Game"
        
        # Check videos data
        assert len(data["videos"]) == 2
        assert data["videos"][0]["id"] == "123456789"
        assert data["videos"][0]["title"] == "Test Video 1"
        assert data["videos"][1]["id"] == "987654321"
        assert data["videos"][1]["title"] == "Test Video 2"

def test_search_videos_with_limit(test_client, mock_twitch_game, mock_twitch_videos):
    """Test the /api/twitch/search endpoint with a limit parameter"""
    # Configure the mocks for the HTTP calls
    with patch('httpx.AsyncClient.get') as mock_get, \
         patch('backend.app.repositories.twitch_repository.TwitchRepository.get_cached_game_search') as mock_cache:
        
        # Ensure the cache is not used for this test
        mock_cache.return_value = None
        
        # Setup the responses for the two API calls
        mock_get.side_effect = [
            MagicMock(json=MagicMock(return_value=mock_twitch_game)),
            MagicMock(json=MagicMock(return_value={"data": mock_twitch_videos["data"][:1]}))  # Return only the first video
        ]
        
        # Configure test data
        headers = {"Authorization": "Bearer test_token"}
        
        # Call the endpoint with limit=1
        response = test_client.get("/api/twitch/search?game_name=Test%20Game&limit=1&use_cache=false", headers=headers)
        
        # Log debugging information
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        
        # Check that only one video was returned
        assert len(data["videos"]) == 1
        assert data["videos"][0]["id"] == "123456789"

def test_search_videos_game_not_found(test_client):
    """Test the /api/twitch/search endpoint when the game is not found"""
    # Configure the mock to simulate an empty response from the Twitch API
    with patch('httpx.AsyncClient.get') as mock_get:
        empty_response = MagicMock()
        empty_response.json.return_value = {"data": []}
        mock_get.return_value = empty_response
        
        # Configure test data
        headers = {"Authorization": "Bearer test_token"}
        
        # Call the endpoint
        response = test_client.get("/api/twitch/search?game_name=NonexistentGame", headers=headers)
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response - should return 200 with empty results
        assert response.status_code == 200
        data = response.json()
        
        # Check for empty game with default values
        assert data["game"]["id"] == "0"
        assert data["game"]["name"] == "NonexistentGame"
        assert data["game"]["box_art_url"] == ""
        
        # Check for empty videos list
        assert len(data["videos"]) == 0 