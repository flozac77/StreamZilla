from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TwitchUser(BaseModel):
    id: str
    login: str
    display_name: str
    profile_image_url: str
    email: Optional[str] = None

class TwitchToken(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    token_type: str
    scope: list[str]

class TwitchVideo(BaseModel):
    id: str
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: str
    published_at: str
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
    game: TwitchGame
    videos: List[TwitchVideo]
    last_updated: str 