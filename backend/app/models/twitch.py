from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

class SearchParams(BaseModel):
    model_config = ConfigDict(title="Paramètres de recherche")
    game_name: str = Field(..., min_length=1, max_length=100, description="Nom du jeu à rechercher")
    limit: int = Field(default=100, ge=1, le=100, description="Nombre maximum de résultats à retourner")
    cursor: Optional[str] = None

class TwitchUser(BaseModel):
    model_config = ConfigDict(title="Utilisateur Twitch")
    id: str
    login: str
    display_name: str
    email: str
    created_at: datetime

class TwitchToken(BaseModel):
    model_config = ConfigDict(
        title="Token Twitch",
        json_schema_extra={
            "example": {
                "access_token": "abcdef123456",
                "expires_at": "2024-03-25T12:00:00",
                "token_type": "bearer",
                "created_at": "2024-03-25T10:00:00",
                "last_used": "2024-03-25T11:00:00",
                "is_valid": True
            }
        }
    )
    
    access_token: str
    expires_at: datetime
    token_type: str = "bearer"
    is_valid: bool = True
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

class TwitchVideo(BaseModel):
    model_config = ConfigDict(title="Vidéo Twitch")
    id: str
    user_name: str
    title: str
    url: str
    view_count: Optional[int] = None
    duration: str
    created_at: str
    language: str
    thumbnail_url: str
    game_id: Optional[str] = None
    game_name: Optional[str] = None
    type: Optional[str] = None  # Pour différencier les lives des archives

class TwitchGame(BaseModel):
    model_config = ConfigDict(title="Jeu Twitch")
    id: str
    name: str
    box_art_url: str

class TwitchSearchResult(BaseModel):
    model_config = ConfigDict(title="Résultat de recherche Twitch")
    game_name: str
    game: Optional[TwitchGame]
    videos: List[TwitchVideo]
    total_count: int
    last_updated: datetime
    pagination: Dict[str, Optional[str]]  # Contient le curseur pour la pagination 