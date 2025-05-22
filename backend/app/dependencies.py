from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from functools import lru_cache

from backend.app.services.twitch_service import TwitchService
from backend.app.config import settings

async def get_db() -> AsyncIOMotorDatabase:
    """
    Dépendance pour obtenir une connexion à la base de données MongoDB.
    Crée une nouvelle connexion par requête pour éviter
    l'utilisation d'un event loop fermé en serverless.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client[settings.MONGODB_DB_NAME]

async def get_twitch_service() -> TwitchService:
    """Get Twitch service instance"""
    service = TwitchService()
    try:
        yield service
    finally:
        await service.close()

async def get_twitch_token(authorization: Optional[str] = Header(None)) -> str:
    """Get token from Authorization header"""
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")