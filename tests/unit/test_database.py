import pytest


def test_mongodb_not_connected_by_default():
    from backend.app.database import MongoDB
    db = MongoDB()
    assert db.client is None
    assert db.db is None


def test_get_db_raises_when_not_connected():
    from backend.app.database import MongoDB
    db = MongoDB()
    with pytest.raises(RuntimeError, match="not connected"):
        db.get_db()


@pytest.mark.asyncio
async def test_connect_sets_client_and_db():
    from backend.app.database import MongoDB
    db = MongoDB()
    await db.connect()
    try:
        assert db.client is not None
        assert db.db is not None
        assert db.get_db() is db.db
    finally:
        await db.disconnect()
    assert db.client is None
    assert db.db is None


def test_module_level_singleton_exists():
    from backend.app import database
    assert hasattr(database, "mongodb")
    assert isinstance(database.mongodb, database.MongoDB)
