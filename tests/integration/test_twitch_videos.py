import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.main import app

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_twitch_videos():
    """Provides a simulated response from the Twitch API for videos."""
    return {
        "data": [
            {
                "id": "video1",
                "user_id": "12345",
                "user_login": "test_user",
                "user_name": "Test User",
                "title": "Test Video",
                "description": "This is a test video",
                "created_at": "2024-01-01T12:00:00Z",
                "published_at": "2024-01-01T12:30:00Z",
                "url": "https://twitch.tv/videos/video1",
                "thumbnail_url": "https://static-cdn.jtvnw.net/cf_vods/d1m7jfoe9zdc1j/test.jpg",
                "viewable": "public",
                "view_count": 1000,
                "language": "fr",
                "type": "archive",
                "duration": "1h30m20s"
            },
            {
                "id": "video2",
                "user_id": "12345",
                "user_login": "test_user",
                "user_name": "Test User",
                "title": "Second Test Video",
                "description": "Another test video",
                "created_at": "2024-01-02T15:00:00Z",
                "published_at": "2024-01-02T15:30:00Z",
                "url": "https://twitch.tv/videos/video2",
                "thumbnail_url": "https://static-cdn.jtvnw.net/cf_vods/d1m7jfoe9zdc1j/test2.jpg",
                "viewable": "public",
                "view_count": 500,
                "language": "fr",
                "type": "highlight",
                "duration": "45m10s"
            }
        ]
    }

@pytest.fixture
def mock_twitch_user_response():
    """Fournit une réponse simulée de l'API Twitch pour un utilisateur."""
    return {
        "data": [
            {
                "id": "12345",
                "login": "test_user",
                "display_name": "Test User",
                "type": "",
                "broadcaster_type": "partner",
                "description": "Test description",
                "profile_image_url": "https://example.com/image.jpg",
                "offline_image_url": "",
                "view_count": 10000,
                "email": "test@example.com",
                "created_at": "2023-01-01T00:00:00Z"
            }
        ]
    }

def test_get_user_videos_success(test_client, mock_twitch_videos):
    """
    Test that the /api/twitch/user/videos endpoint correctly returns the list of videos
    when the Twitch API call succeeds.
    """
    # Configure the mock to simulate the Twitch API response
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = mock_twitch_videos
        mock_get.return_value = get_response

        # Call the endpoint
        response = test_client.get(
            "/api/twitch/user/videos", 
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
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify details of the first video
        assert data[0]["id"] == "video1"
        assert data[0]["title"] == "Test Video"
        assert data[0]["user_id"] == "12345"
        assert data[0]["view_count"] == 1000
        
        # Verify details of the second video
        assert data[1]["id"] == "video2"
        assert data[1]["title"] == "Second Test Video"
        assert data[1]["type"] == "highlight"

def test_get_user_videos_error(test_client):
    """
    Test that the /api/twitch/user/videos endpoint correctly handles errors
    when the Twitch API call fails.
    """
    # Configure the mock to simulate a Twitch API error
    with patch('httpx.AsyncClient.get') as mock_get:
        # Simulate an exception
        mock_get.side_effect = Exception("Twitch API unavailable")

        # Call the endpoint
        response = test_client.get(
            "/api/twitch/user/videos", 
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify that the error is handled correctly
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Twitch API unavailable" in data["detail"]

def test_get_user_videos_no_auth(test_client):
    """
    Test that the /api/twitch/user/videos endpoint returns videos even without an auth token
    (because we use a default token for tests).
    """
    # Configure the mock to simulate the Twitch API response
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = {"data": []}  # No videos
        mock_get.return_value = get_response

        # Call the endpoint without an auth token
        response = test_client.get("/api/twitch/user/videos")
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        
        # Verify the response - should succeed with an empty array
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

def test_find_user_by_login_success(test_client, mock_twitch_user_response):
    """
    Test that the /api/twitch/user/find endpoint correctly finds a user
    by their login when the Twitch API call succeeds.
    """
    # Configure the mock to simulate the Twitch API response
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = mock_twitch_user_response
        mock_get.return_value = get_response

        # Call the endpoint
        response = test_client.get(
            "/api/twitch/user/find?login=test_user", 
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
        assert data["id"] == "12345"
        assert data["login"] == "test_user"
        assert data["display_name"] == "Test User"
        assert "profile_image_url" in data

def test_find_user_by_login_not_found(test_client):
    """
    Test that the /api/twitch/user/find endpoint correctly handles the case where
    the user is not found.
    """
    # Configure the mock to simulate a Twitch API response with no data
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = {"data": []}
        mock_get.return_value = get_response

        # Call the endpoint
        response = test_client.get(
            "/api/twitch/user/find?login=nonexistent_user", 
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Log for debugging
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify that the error is handled correctly
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() 