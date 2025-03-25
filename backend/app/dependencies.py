from fastapi import Depends, HTTPException, status
from backend.app.services.twitch_service import TwitchService
from backend.app.config import settings

async def get_twitch_service() -> TwitchService:
    """Get Twitch service instance"""
    return TwitchService()

async def get_twitch_token() -> str:
    """Get Twitch token from environment for testing"""
    if not settings.TWITCH_ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Twitch access token not found"
        )
    return settings.TWITCH_ACCESS_TOKEN 