import pytest
from datetime import datetime
from backend.app.models.twitch import TwitchUser, TwitchToken
from backend.app.repositories.twitch_repository import TwitchRepository
from backend.app.database import get_db  # Importer la fonction get_db


@pytest.mark.asyncio
async def test_create_user():
    """Test creating a new user"""
    repo = TwitchRepository()
    
    user = TwitchUser(
        id="12345",
        login="test_user",
        display_name="Test User",
        profile_image_url="https://example.com/image.jpg",
        email="test@example.com",
        created_at=datetime.utcnow()
    )
    
    created_user = await repo.create_user(user)
    assert created_user.id == user.id
    assert created_user.login == user.login
    
    # Verify user exists in database
    db_user = await repo.get_user_by_id(user.id)
    assert db_user is not None
    assert db_user.id == user.id

# Continue with other tests...