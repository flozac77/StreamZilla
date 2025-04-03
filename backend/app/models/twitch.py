from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class SearchParams(BaseModel):
    model_config = ConfigDict(title="Paramètres de recherche")
    game_name: str = Field(..., min_length=1, max_length=100, description="Nom du jeu à rechercher")
    limit: int = Field(default=100, ge=1, le=100, description="Nombre maximum de résultats à retourner")

class TwitchUser(BaseModel):
    model_config = ConfigDict(title="Utilisateur Twitch")
    id: str
    login: str
    display_name: str
    type: str
    broadcaster_type: str
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int
    email: str
    created_at: datetime

class TwitchToken(BaseModel):
    model_config = ConfigDict(title="Token Twitch")
    access_token: str
    refresh_token: str
    expires_in: int
    scope: List[str]
    token_type: str

class TwitchVideo(BaseModel):
    model_config = ConfigDict(title="Vidéo Twitch")
    id: str
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: datetime
    published_at: datetime
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: str
    duration: str

class TwitchGame(BaseModel):
    model_config = ConfigDict(title="Jeu Twitch")
    id: str
    name: str
    box_art_url: str

class TwitchSearchResult(BaseModel):
    model_config = ConfigDict(title="Résultat de recherche Twitch")
    game_name: str = Field(..., description="Nom du jeu recherché")
    game: Optional[TwitchGame] = None
    videos: List[TwitchVideo] = Field(default_factory=list)
    total_count: int = Field(default=0, description="Nombre total de vidéos disponibles")
    last_updated: datetime = Field(default_factory=datetime.utcnow) 