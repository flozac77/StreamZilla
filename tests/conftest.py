import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.main import app
from backend.app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def test_client():
    """Create a test client for testing the API."""
    logger.debug("Creating test client")
    with TestClient(app) as client:
        # Override normal dependencies with test dependencies
        # Configure the client for testing
        client.headers = {"Content-Type": "application/json"}
        yield client
    logger.debug("Test client closed")

@pytest.fixture
async def test_db():
    """Create a test database."""
    logger.debug("Creating test database connection")
    # Use test database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME + "_test"]
    
    # Clean database at the beginning of the test
    await db.users.delete_many({})
    await db.tokens.delete_many({})
    await db.games.delete_many({})
    await db.search_cache.delete_many({})
    
    yield db
    
    # Clean database at the end of the test
    await db.users.delete_many({})
    await db.tokens.delete_many({})
    await db.games.delete_many({})
    await db.search_cache.delete_many({})
    client.close()
    logger.debug("Test database connection closed")

@pytest.fixture
def mock_twitch_response():
    """Return a mock response for Twitch API."""
    return {
        "data": [{
            "id": "12345",
            "login": "test_user",
            "display_name": "Test User",
            "type": "",
            "broadcaster_type": "",
            "description": "Test description",
            "profile_image_url": "https://example.com/image.jpg",
            "offline_image_url": "",
            "view_count": 0,
            "email": "test@example.com",
            "created_at": "2023-01-01T00:00:00Z"
        }]
    }

@pytest.fixture
def mock_twitch_token():
    """Return a mock token response."""
    return {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 3600,
        "scope": ["user:read:email"],
        "token_type": "bearer"
    }

@pytest.fixture
def mock_twitch_game():
    """Return a mock game response."""
    return {
        "data": [{
            "id": "12345",
            "name": "Test Game",
            "box_art_url": "https://example.com/game.jpg"
        }]
    }

@pytest.fixture
def mock_twitch_videos():
    """Return a mock videos response."""
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