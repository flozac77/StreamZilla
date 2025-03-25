from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from functools import lru_cache

from backend.app.services.twitch_service import TwitchService
from backend.app.config import settings

# MongoDB connection globale
_mongodb_client: Optional[AsyncIOMotorClient] = None

async def get_db() -> AsyncIOMotorDatabase:
    """
    Dépendance pour obtenir une connexion à la base de données MongoDB.
    La connexion est réutilisée entre les requêtes.
    """
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    return _mongodb_client[settings.MONGODB_DB_NAME]

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
    raise HTTPException(status_code=401, detail="Invalid or missing token") 