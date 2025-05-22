import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import unittest.mock

from backend.app.models.twitch import TwitchToken
from backend.app.repositories.token_repository import TokenRepository

# Mock de AsyncIOMotorDatabase
@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.mark.asyncio
async def test_save_token_success(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_token_data = {
        "access_token": "test_token",
        "expires_in": 3600,
        "token_type": "bearer",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    token = TwitchToken(**mock_token_data)

    mock_insert_one = AsyncMock()
    mock_db.twitch_tokens.insert_one = mock_insert_one

    # Act
    await repo.save_token(token)

    # Assert
    mock_insert_one.assert_awaited_once()
    # On vérifie que l'objet inséré ressemble à un dictionnaire de token avec created_at
    inserted_data = mock_insert_one.call_args[0][0]
    assert isinstance(inserted_data, dict)
    assert "access_token" in inserted_data and inserted_data["access_token"] == "test_token"
    assert "created_at" in inserted_data
    assert isinstance(inserted_data["created_at"], datetime)

@pytest.mark.asyncio
async def test_save_token_exception(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_token_data = {
        "access_token": "test_token",
        "expires_in": 3600,
        "token_type": "bearer",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    token = TwitchToken(**mock_token_data)

    mock_insert_one = AsyncMock(side_effect=Exception("DB Error"))
    mock_db.twitch_tokens.insert_one = mock_insert_one

    # Act & Assert
    with pytest.raises(Exception, match="DB Error"):
        await repo.save_token(token)
    mock_insert_one.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_current_token_found(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    valid_expires_at = datetime.utcnow() + timedelta(hours=1)
    mock_token_data = {
        "_id": "some_id", # Ajouter un _id comme si ça venait de Mongo
        "access_token": "valid_token",
        "expires_in": 3600,
        "token_type": "bearer",
        "expires_at": valid_expires_at,
        "is_valid": True,
        "created_at": datetime.utcnow()
    }
    mock_find_one = AsyncMock(return_value=mock_token_data)
    mock_db.twitch_tokens.find_one = mock_find_one

    # Act
    token = await repo.get_current_token()

    # Assert
    mock_find_one.assert_awaited_once()
    assert isinstance(token, TwitchToken)
    assert token.access_token == "valid_token"

@pytest.mark.asyncio
async def test_get_current_token_not_found(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_find_one = AsyncMock(return_value=None)
    mock_db.twitch_tokens.find_one = mock_find_one

    # Act
    token = await repo.get_current_token()

    # Assert
    mock_find_one.assert_awaited_once()
    assert token is None

@pytest.mark.asyncio
async def test_get_current_token_exception(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_find_one = AsyncMock(side_effect=Exception("DB Error"))
    mock_db.twitch_tokens.find_one = mock_find_one

    # Act
    token = await repo.get_current_token()

    # Assert
    mock_find_one.assert_awaited_once()
    # En cas d'exception, get_current_token doit retourner None
    assert token is None

@pytest.mark.asyncio
async def test_update_last_used_success(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_token_data = {
        "access_token": "token_to_update",
        "expires_in": 3600,
        "token_type": "bearer",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    token = TwitchToken(**mock_token_data)

    mock_update_one = AsyncMock()
    mock_db.twitch_tokens.update_one = mock_update_one

    # Act
    await repo.update_last_used(token)

    # Assert
    mock_update_one.assert_awaited_once_with(
        {"access_token": token.access_token},
        {"$set": unittest.mock.ANY}
    )
    # Vérifier que la date insérée est proche de maintenant
    inserted_data = mock_update_one.call_args[0][1]['$set']['last_used']
    assert isinstance(inserted_data, datetime)
    assert datetime.utcnow() - inserted_data < timedelta(seconds=5)

@pytest.mark.asyncio
async def test_update_last_used_exception(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_token_data = {
        "access_token": "token_to_update",
        "expires_in": 3600,
        "token_type": "bearer",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    token = TwitchToken(**mock_token_data)

    mock_update_one = AsyncMock(side_effect=Exception("DB Error"))
    mock_db.twitch_tokens.update_one = mock_update_one

    # Act
    await repo.update_last_used(token)

    # Assert
    mock_update_one.assert_awaited_once()
    # Pas d'assertion d'exception car la méthode log l'erreur mais ne la relève pas

@pytest.mark.asyncio
async def test_invalidate_token_success(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_token_data = {
        "access_token": "token_to_invalidate",
        "expires_in": 3600,
        "token_type": "bearer",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    token = TwitchToken(**mock_token_data)

    mock_update_one = AsyncMock()
    mock_db.twitch_tokens.update_one = mock_update_one

    # Act
    await repo.invalidate_token(token)

    # Assert
    mock_update_one.assert_awaited_once_with(
        {"access_token": token.access_token},
        {"$set": {"is_valid": False}}
    )

@pytest.mark.asyncio
async def test_invalidate_token_exception(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_token_data = {
        "access_token": "token_to_invalidate",
        "expires_in": 3600,
        "token_type": "bearer",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    token = TwitchToken(**mock_token_data)

    mock_update_one = AsyncMock(side_effect=Exception("DB Error"))
    mock_db.twitch_tokens.update_one = mock_update_one

    # Act & Assert
    with pytest.raises(Exception, match="DB Error"):
        await repo.invalidate_token(token)
    mock_update_one.assert_awaited_once()

@pytest.mark.asyncio
async def test_cleanup_old_tokens_success(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_delete_many = AsyncMock()
    mock_delete_many.return_value.deleted_count = 5 # Simuler 5 documents supprimés
    mock_db.twitch_tokens.delete_many = mock_delete_many

    # Act
    await repo.cleanup_old_tokens(days=10)

    # Assert
    mock_delete_many.assert_awaited_once()
    # Vérifier la requête de suppression (approx)
    delete_query = mock_delete_many.call_args[0][0]
    assert "is_valid" in delete_query and delete_query["is_valid"] is False
    assert "created_at" in delete_query and "$lt" in delete_query["created_at"]
    # Vérifier que la date de coupure est correcte
    cutoff_date = delete_query["created_at"]["$lt"]
    assert isinstance(cutoff_date, datetime)
    assert datetime.utcnow() - cutoff_date < timedelta(days=11)
    assert datetime.utcnow() - cutoff_date > timedelta(days=9)

@pytest.mark.asyncio
async def test_cleanup_old_tokens_exception(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_delete_many = AsyncMock(side_effect=Exception("DB Error"))
    mock_db.twitch_tokens.delete_many = mock_delete_many

    # Act & Assert
    with pytest.raises(Exception, match="DB Error"):
        await repo.cleanup_old_tokens(days=10)
    mock_delete_many.assert_awaited_once()

@pytest.mark.asyncio
async def test_initialize_success(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_create_index = AsyncMock()
    mock_db.twitch_tokens.create_index = mock_create_index

    # Act
    await repo.initialize()

    # Assert
    # On s'attend à deux appels à create_index
    assert mock_create_index.call_count == 2
    # On peut vérifier les arguments des appels si nécessaire, mais le count est suffisant pour la couverture de base

@pytest.mark.asyncio
async def test_initialize_exception(mock_db):
    # Arrange
    repo = TokenRepository(db=mock_db)
    mock_create_index = AsyncMock(side_effect=Exception("DB Error"))
    mock_db.twitch_tokens.create_index = mock_create_index

    # Act & Assert
    with pytest.raises(Exception, match="DB Error"):
        await repo.initialize()
    # On s'attend à au moins un appel avant l'exception (le premier create_index)
    assert mock_create_index.call_count >= 1 