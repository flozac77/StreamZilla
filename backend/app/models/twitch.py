from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SearchParams(BaseModel):
    game_name: str = Field(..., min_length=1, max_length=100, description="Nom du jeu à rechercher")
    limit: int = Field(default=10, ge=1, le=100, description="Nombre maximum de résultats à retourner")

class TwitchUser(BaseModel):
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
    access_token: str
    refresh_token: str
    expires_in: int
    scope: List[str]
    token_type: str

class TwitchVideo(BaseModel):
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
    id: str
    name: str
    box_art_url: str

class TwitchSearchResult(BaseModel):
    game: Optional[TwitchGame] = None
    videos: List[TwitchVideo] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow) 