import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app

client = TestClient(app)

@pytest.fixture
def mock_video_response():
    return {
        "game_name": "Minecraft",
        "videos": [
            {
                "id": "1234",
                "user_name": "TestStreamer",
                "title": "Test Stream",
                "view_count": 1000,
                "duration": "1h2m3s",
                "url": "https://twitch.tv/videos/1234",
                "type": "archive"
            }
        ],
        "last_updated": "2024-03-25T12:00:00Z"
    }

def test_search_endpoint_exists():
    """Vérifie que l'endpoint de recherche existe"""
    response = client.get("/api/search?game_name=Minecraft")
    assert response.status_code != 404, "L'endpoint /api/search n'existe pas"

@patch('backend.app.services.twitch.video_service.TwitchVideoService.search_videos')
def test_search_basic_functionality(mock_search):
    """Test la fonctionnalité basique de recherche"""
    mock_search.return_value = mock_video_response()
    
    response = client.get("/api/search?game_name=Minecraft")
    assert response.status_code == 200
    data = response.json()
    
    # Vérifie la structure de la réponse
    assert "game_name" in data, "La réponse devrait contenir game_name"
    assert "videos" in data, "La réponse devrait contenir videos"
    assert "last_updated" in data, "La réponse devrait contenir last_updated"
    
    # Vérifie le contenu
    assert data["game_name"] == "Minecraft"
    assert len(data["videos"]) > 0
    
    # Vérifie la structure d'une vidéo
    video = data["videos"][0]
    required_fields = ["id", "user_name", "title", "view_count", "duration", "url"]
    for field in required_fields:
        assert field in video, f"La vidéo devrait contenir le champ {field}"

def test_search_required_params():
    """Vérifie que le paramètre game_name est requis"""
    response = client.get("/api/search")
    assert response.status_code == 422, "La requête devrait échouer sans game_name"

@patch('backend.app.services.twitch.video_service.TwitchVideoService.search_videos')
def test_search_with_cache(mock_search):
    """Test la fonctionnalité de cache"""
    mock_search.return_value = mock_video_response()
    
    # Premier appel avec cache
    response1 = client.get("/api/search?game_name=Minecraft&use_cache=true")
    assert response1.status_code == 200
    
    # Deuxième appel avec cache
    response2 = client.get("/api/search?game_name=Minecraft&use_cache=true")
    assert response2.status_code == 200
    
    # Vérifie que le mock n'a été appelé qu'une fois
    assert mock_search.call_count == 1, "Le cache devrait éviter les appels répétés"

@patch('backend.app.services.twitch.video_service.TwitchVideoService.search_videos')
def test_search_error_handling(mock_search):
    """Test la gestion des erreurs"""
    mock_search.side_effect = Exception("API Error")
    
    response = client.get("/api/search?game_name=Minecraft")
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data, "Les erreurs devraient avoir un champ 'detail'" 