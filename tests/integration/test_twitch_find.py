import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.main import app

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_twitch_user_response():
    """Provides a mock response from Twitch API for a user."""
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
    Test that the /api/twitch/user/find endpoint correctly handles the case
    where the user is not found.
    """
    # Configure the mock to simulate an empty response from the Twitch API
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