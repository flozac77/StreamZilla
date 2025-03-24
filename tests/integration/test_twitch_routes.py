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
    response = test_client.get("/api/twitch/auth/url")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "id.twitch.tv/oauth2/authorize" in data["url"]

def test_callback_endpoint(test_client, mock_twitch_token, mock_twitch_response):
    """Test the /api/twitch/auth/callback endpoint"""
    # Configure mocks for HTTP calls
    with patch('httpx.AsyncClient.post') as mock_post, \
         patch('httpx.AsyncClient.get') as mock_get:
        
        # Mock token exchange
        post_response = MagicMock()
        post_response.json.return_value = mock_twitch_token
        mock_post.return_value = post_response
        
        # Mock user info
        get_response = MagicMock()
        get_response.json.return_value = mock_twitch_response
        mock_get.return_value = get_response

        # Call the endpoint
        response = test_client.get("/api/twitch/auth/callback?code=test_code")
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["id"] == "12345"
        assert data["user"]["login"] == "test_user"

def test_user_info_endpoint(test_client, mock_twitch_response):
    """Test the /api/twitch/user/info endpoint"""
    # Configure the mock for the HTTP call
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = mock_twitch_response
        mock_get.return_value = get_response

        # Call the endpoint
        response = test_client.get("/api/twitch/user/info", headers={"Authorization": "Bearer test_token"})
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
    # Configure test data
    mock_videos = {
        "data": [{
            "id": "video1",
            "title": "Test Video",
            "description": "Test Description",
            "created_at": "2024-01-01T00:00:00Z",
            "url": "https://example.com/video",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "view_count": 100,
            "duration": "1h"
        }]
    }

    # Configure the mock for the HTTP call
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = mock_videos
        mock_get.return_value = get_response

        # Call the endpoint
        response = test_client.get("/api/twitch/user/videos", headers={"Authorization": "Bearer test_token"})
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "video1"
        assert data[0]["title"] == "Test Video"

def test_stream_key_endpoint(test_client):
    """Test the /api/twitch/user/stream-key endpoint"""
    # Configure test data
    mock_stream_key = {
        "data": [{
            "stream_key": "test-stream-key"
        }]
    }

    # Configure the mock for the HTTP call
    with patch('httpx.AsyncClient.get') as mock_get:
        get_response = MagicMock()
        get_response.json.return_value = mock_stream_key
        mock_get.return_value = get_response

        # Call the endpoint
        response = test_client.get("/api/twitch/user/stream-key", headers={"Authorization": "Bearer test_token"})
        logger.debug(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response content: {response.content.decode('utf-8')}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["data"][0]["stream_key"] == "test-stream-key" 