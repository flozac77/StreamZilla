import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.app.repositories.twitch_repository import TwitchRepository
from backend.app.models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult
from datetime import datetime, timedelta

@pytest.fixture
def mock_settings():
    """Fixture pour mocker les settings."""
    with patch('backend.app.repositories.twitch_repository.settings') as mock:
        mock.MONGODB_URL = "mongodb://test:27017"
        mock.MONGODB_DB_NAME = "test_db"
        yield mock

@pytest.fixture
def mock_client():
    """Fixture pour mocker le client MongoDB."""
    with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock:
        yield mock

@pytest.fixture
def repository(mock_settings, mock_client):
    """Fixture pour créer une instance de TwitchRepository."""
    repo = TwitchRepository()
    yield repo
    repo.close()

@pytest.fixture
def sample_user():
    """Fixture pour créer un utilisateur de test."""
    return TwitchUser(
        id="123",
        login="test_user",
        display_name="Test User",
        profile_image_url="http://test.com/image.jpg"
    )

@pytest.fixture
def sample_token():
    """Fixture pour créer un token de test."""
    return TwitchToken(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=3600,
        token_type="bearer",
        scope=["user:read:email"]
    )

@pytest.mark.asyncio
async def test_create_user(repository, sample_user):
    """Test la création d'un utilisateur."""
    # Configurer le mock
    repository.users_collection.insert_one = AsyncMock()
    repository.users_collection.find_one = AsyncMock(return_value=None)
    
    # Appeler la fonction
    result = await repository.create_user(sample_user)
    
    # Vérifier les appels
    repository.users_collection.insert_one.assert_called_once_with(sample_user.model_dump())
    assert result == sample_user

@pytest.mark.asyncio
async def test_get_user_by_id(repository, sample_user):
    """Test la récupération d'un utilisateur par ID."""
    # Configurer le mock
    repository.users_collection.find_one = AsyncMock(return_value=sample_user.model_dump())
    
    # Appeler la fonction
    result = await repository.get_user_by_id("123")
    
    # Vérifier les appels
    repository.users_collection.find_one.assert_called_once_with({"id": "123"})
    assert result == sample_user

@pytest.mark.asyncio
async def test_update_user(repository, sample_user):
    """Test la mise à jour d'un utilisateur."""
    # Configurer les mocks
    repository.users_collection.update_one = AsyncMock()
    repository.users_collection.find_one = AsyncMock(return_value=sample_user.model_dump())
    
    # Appeler la fonction
    result = await repository.update_user("123", display_name="Updated Name")
    
    # Vérifier les appels
    repository.users_collection.update_one.assert_called_once_with(
        {"id": "123"},
        {"$set": {"display_name": "Updated Name"}}
    )
    assert result == sample_user

@pytest.mark.asyncio
async def test_delete_user(repository):
    """Test la suppression d'un utilisateur."""
    # Configurer le mock
    repository.users_collection.delete_one = AsyncMock()
    
    # Appeler la fonction
    await repository.delete_user("123")
    
    # Vérifier l'appel
    repository.users_collection.delete_one.assert_called_once_with({"id": "123"})

@pytest.mark.asyncio
async def test_save_token(repository, sample_token):
    """Test la sauvegarde d'un token."""
    # Configurer le mock
    repository.tokens_collection.update_one = AsyncMock()
    
    # Appeler la fonction
    result = await repository.save_token("123", sample_token)
    
    # Vérifier les appels
    token_dict = sample_token.model_dump()
    token_dict['user_id'] = "123"
    repository.tokens_collection.update_one.assert_called_once_with(
        {"user_id": "123"},
        {"$set": token_dict},
        upsert=True
    )
    assert result == sample_token

@pytest.mark.asyncio
async def test_get_cached_game_search(repository):
    """Test la récupération des résultats de recherche en cache."""
    # Créer des données de test
    game = TwitchGame(id="123", name="test Game", box_art_url="http://test.com/game.jpg")
    videos = [
        TwitchVideo(
            id="1",
            user_id="123",
            user_login="test_user",
            user_name="Test User",
            title="Test Video",
            description="Test Description",
            created_at=datetime.now().isoformat(),  # Convertir en string ISO
            published_at=datetime.now().isoformat(),  # Convertir en string ISO
            url="http://test.com/video",
            thumbnail_url="http://test.com/thumb.jpg",
            viewable="true",  # Convertir en string
            view_count=100,
            language="fr",
            type="archive",
            duration="1h"
        )
    ]
    search_result = TwitchSearchResult(game=game, videos=videos, last_updated=datetime.now().isoformat())
    
    # Configurer le mock
    repository.search_cache_collection.find_one = AsyncMock(return_value={
        "game_name": "test Game",
        "game": game.model_dump(),
        "videos": [v.model_dump() for v in videos],
        "created_at": datetime.now().isoformat()
    })
    
    # Appeler la fonction
    result = await repository.get_cached_game_search("test Game")
    
    # Vérifier les appels
    repository.search_cache_collection.find_one.assert_called_once_with({"game_name": "test Game"})
    assert result.game == game
    assert len(result.videos) == 1
    assert result.videos[0].id == "1"

@pytest.mark.asyncio
async def test_save_game_search_results(repository):
    """Test la sauvegarde des résultats de recherche."""
    # Créer des données de test
    game = TwitchGame(id="123", name="test Game", box_art_url="http://test.com/game.jpg")
    videos = [
        TwitchVideo(
            id="1",
            user_id="123",
            user_login="test_user",
            user_name="Test User",
            title="Test Video",
            description="Test Description",
            created_at=datetime.now().isoformat(),  # Convertir en string ISO
            published_at=datetime.now().isoformat(),  # Convertir en string ISO
            url="http://test.com/video",
            thumbnail_url="http://test.com/thumb.jpg",
            viewable="true",  # Convertir en string
            view_count=100,
            language="fr",
            type="archive",
            duration="1h"
        )
    ]
    
    # Configurer le mock
    repository.search_cache_collection.insert_one = AsyncMock()
    
    # Appeler la fonction
    await repository.save_game_search_results("test Game", game, videos)
    
    # Vérifier l'appel
    repository.search_cache_collection.insert_one.assert_called_once()
    call_args = repository.search_cache_collection.insert_one.call_args[0][0]
    assert call_args["game_name"] == "test Game"
    assert call_args["game"] == game.model_dump()
    assert len(call_args["videos"]) == 1
    assert call_args["videos"][0]["id"] == "1"
    assert "created_at" in call_args 