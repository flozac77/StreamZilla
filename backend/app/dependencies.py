from typing import Optional

from fastapi import HTTPException, Header, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.database import mongodb
from backend.app.services.twitch_service import TwitchService


async def get_db() -> AsyncIOMotorDatabase:
    """Return the shared MongoDB database handle."""
    return mongodb.get_db()


async def get_twitch_service() -> TwitchService:
    """Get Twitch service instance."""
    service = TwitchService()
    try:
        yield service
    finally:
        await service.close()


async def get_twitch_token(authorization: Optional[str] = Header(None)) -> str:
    """Get token from Authorization header."""
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing token",
    )
