from pydantic import BaseModel
from typing import List

class Video(BaseModel):
    id: str
    user_name: str
    title: str
    url: str
    view_count: int
    duration: str

class VideoResponse(BaseModel):
    videos: List[Video]
    game: str
    last_updated: str 