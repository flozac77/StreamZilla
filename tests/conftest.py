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
    
    yield db
    
    # Clean database at the end of the test
    await db.users.delete_many({})
    await db.tokens.delete_many({})
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