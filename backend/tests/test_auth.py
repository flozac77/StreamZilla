import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.services.twitch.auth import TwitchAuthService
from backend.app.repositories.token_repository import TokenRepository

@pytest.fixture
async def mongodb():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.visibrain_test
    yield db
    await client.drop_database("visibrain_test")
    client.close()

@pytest.fixture
async def token_repository(mongodb):
    repo = TokenRepository(mongodb)
    await repo.initialize()
    return repo

@pytest.fixture
async def auth_service(token_repository):
    service = TwitchAuthService(token_repository)
    yield service
    await service.close()

@pytest.mark.asyncio
async def test_generate_token(auth_service):
    token = await auth_service.get_valid_token()
    assert token is not None
    assert token.access_token is not None
    assert token.is_valid is True

@pytest.mark.asyncio
async def test_token_validation(auth_service):
    token = await auth_service.get_valid_token()
    is_valid = await auth_service._is_token_valid(token)
    assert is_valid is True 