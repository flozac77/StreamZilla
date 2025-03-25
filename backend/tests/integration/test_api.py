import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.main import app
from datetime import datetime

# Configuration du logger pour le debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = TestClient(app)

@pytest.fixture
def mock_video_response():
    """Fournit une réponse simulée pour les vidéos"""
    return {
        "game_name": "Minecraft",
        "game": {
            "id": "27471",
            "name": "Minecraft",
            "box_art_url": "https://static-cdn.jtvnw.net/ttv-boxart/27471-{width}x{height}.jpg"
        },
        "videos": [
            {
                "id": "1234",
                "user_name": "TestStreamer",
                "title": "Test Stream",
                "view_count": 1000,
                "duration": "1h2m3s",
                "url": "https://twitch.tv/videos/1234",
                "thumbnail_url": "https://example.com/thumbnail.jpg",
                "type": "archive"
            }
        ],
        "last_updated": "2024-03-25T12:00:00Z"
    }

# Tests de recherche
def test_search_endpoint_exists():
    """Vérifie que l'endpoint de recherche existe"""
    response = client.get("/api/search?game_name=Minecraft")
    assert response.status_code != 404, "L'endpoint /api/search n'existe pas"



def test_search_required_params():
    """Vérifie que le paramètre game_name est requis"""
    response = client.get("/api/search")
    assert response.status_code == 422, "La requête devrait échouer sans game_name"


@patch('backend.app.services.twitch_service.TwitchService.search_videos_by_game')
def test_search_error_handling(mock_search):
    """Test la gestion des erreurs"""
    mock_search.side_effect = Exception("API Error")
    
    response = client.get("/api/search?game_name=Minecraft")
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data, "Les erreurs devraient avoir un champ 'detail'" 