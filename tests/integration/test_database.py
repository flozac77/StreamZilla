import pytest
from datetime import datetime
from backend.app.models.twitch import TwitchUser, TwitchToken
from backend.app.repositories.twitch_repository import TwitchRepository
from backend.app.database import get_db,get_async_db  # Importer la fonction get_db

# --- Tests CRUD MongoDB basiques ---
def test_sync_db_crud():
    db = get_db()
    coll_name = "__test_sync__"
    coll = db[coll_name]
    # nettoyage éventuel
    if coll_name in db.list_collection_names():
        coll.drop()
    # Create
    result = coll.insert_one({"foo": "bar"})
    # Read
    doc = coll.find_one({"_id": result.inserted_id})
    assert doc["foo"] == "bar"
    # Cleanup
    coll.drop()

@pytest.mark.asyncio
async def test_async_db_crud():
    db = await get_async_db()
    coll_name = "__test_async__"
    coll = db[coll_name]
    # nettoyage éventuel
    existing = await db.list_collection_names()
    if coll_name in existing:
        await coll.drop()
    # Create
    result = await coll.insert_one({"ping": "pong"})
    # Read
    doc = await coll.find_one({"_id": result.inserted_id})
    assert doc["ping"] == "pong"
    # Cleanup
    await coll.drop()