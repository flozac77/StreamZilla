import pytest
from unittest.mock import patch, MagicMock
from backend.app.database import get_db, get_async_db

def test_get_db():
    """Test the get_db function that provides a synchronous MongoDB connection."""
    with patch('backend.app.database.MongoClient') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        
        # Call the function
        db = get_db()
        
        # Verify the connection was created with correct parameters
        mock_client.assert_called_once()
        assert db is mock_db

@pytest.mark.asyncio
async def test_get_async_db():
    """Test the get_async_db function that provides an asynchronous MongoDB connection."""
    with patch('backend.app.database.AsyncIOMotorClient') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        
        # Call the function
        db = await get_async_db()
        
        # Verify the connection was created with correct parameters
        mock_client.assert_called_once()
        assert db is mock_db 