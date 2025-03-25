from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TwitchToken(BaseModel):
    access_token: str
    expires_at: datetime
    token_type: str = "bearer"
    is_valid: bool = True
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "abcdef123456",
                "expires_at": "2024-03-25T12:00:00",
                "token_type": "bearer",
                "created_at": "2024-03-25T10:00:00",
                "last_used": "2024-03-25T11:00:00",
                "is_valid": True
            }
        } 