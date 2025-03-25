from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query, status
from fastapi.responses import RedirectResponse
from cachetools import TTLCache, cached
from typing import Optional, List
from pydantic import Field
import logging
from fastapi_limiter.depends import RateLimiter
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.config import settings
from backend.app.services.twitch_service import TwitchService
from backend.app.models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult, SearchParams
from backend.app.dependencies import get_twitch_service, get_twitch_token, get_db
from backend.app.services.twitch.auth import TwitchAuthService
from backend.app.repositories.token_repository import TokenRepository

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Init router
router = APIRouter()

# Cache for Twitch data
twitch_cache = TTLCache(maxsize=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL)

# Dependency to get TwitchService
async def get_twitch_service():
    service = TwitchService()
    try:
        yield service
    finally:
        await service.close()

# Dependency to get token from Authorization header
def get_token(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return "test_token"  # Default value for tests

# Conditional rate limiter based on environment
def get_rate_limiter(times: int, minutes: int):
    if settings.ENVIRONMENT == "dev":
        # En dev, pas de rate limiting
        return lambda: None
    else:
        # En prod, utiliser le rate limiter
        return RateLimiter(times=times, minutes=minutes)

@router.get("/auth/url", response_model=str)
async def get_auth_url(
    service: TwitchService = Depends(get_twitch_service),
    rate_limit: None = Depends(get_rate_limiter(times=5, minutes=1))
):
    """Get Twitch authentication URL"""
    try:
        return await service.get_auth_url()
    except Exception as e:
        logger.error(f"Error getting auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate auth URL")

@router.get("/auth/callback", response_model=TwitchToken)
async def auth_callback(
    code: str,
    service: TwitchService = Depends(get_twitch_service),
    rate_limit: None = Depends(RateLimiter(times=5, minutes=1))
):
    """Handle OAuth callback and exchange code for token"""
    try:
        return await service.exchange_code_for_token(code)
    except Exception as e:
        logger.error(f"Error exchanging code for token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to exchange code for token")

@router.get("/user/info", response_model=TwitchUser)
async def get_user_info(
    token: str = Depends(get_twitch_token),
    service: TwitchService = Depends(get_twitch_service),
    rate_limit: None = Depends(RateLimiter(times=10, minutes=1))
):
    """Get current user information"""
    try:
        return await service.get_user_info(token)
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

@router.get("/user/videos", response_model=List[TwitchVideo])
async def get_user_videos(
    user_id: str,
    token: str = Depends(get_twitch_token),
    service: TwitchService = Depends(get_twitch_service),
    rate_limit: None = Depends(RateLimiter(times=10, minutes=1))
):
    """Get videos for a user"""
    try:
        return await service.get_user_videos(user_id, token)
    except Exception as e:
        logger.error(f"Error getting user videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user videos")

@router.get("/user/stream-key")
async def get_stream_key(
    user_id: str,
    token: str = Depends(get_twitch_token),
    service: TwitchService = Depends(get_twitch_service),
    rate_limit: None = Depends(RateLimiter(times=5, minutes=1))
):
    """Get user's stream key"""
    try:
        return await service.get_stream_key(user_id, token)
    except Exception as e:
        logger.error(f"Error getting stream key: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stream key")

@router.get("/search", response_model=TwitchSearchResult)
async def search_videos_by_game(
    game_name: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=100),
    use_cache: bool = Query(default=True),
    service: TwitchService = Depends(get_twitch_service),
    rate_limit: None = Depends(get_rate_limiter(times=10, minutes=1))
):
    """Search videos by game name"""
    try:
        return await service.search_videos_by_game(game_name, None, limit=limit, use_cache=use_cache)
    except Exception as e:
        logger.error(f"Error searching videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search videos")

async def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> TwitchAuthService:
    token_repository = TokenRepository(db)
    return TwitchAuthService(token_repository)

@router.get("/auth/test")
async def test_auth(auth_service: TwitchAuthService = Depends(get_auth_service)):
    """
    Test l'authentification Twitch en générant/validant un token.
    """
    try:
        token = await auth_service.get_valid_token()
        return {
            "status": "success",
            "token_type": token.token_type,
            "expires_at": token.expires_at.isoformat(),
            "is_valid": token.is_valid,
            "token_preview": f"{token.access_token[:8]}..."  # Ne jamais exposer le token complet
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/videos/{game_name}")
async def get_videos_by_game(
    game_name: str,
    auth_service: TwitchAuthService = Depends(get_auth_service)
):
    """
    Récupère les vidéos pour un jeu donné.
    """
    try:
        token = await auth_service.get_valid_token()
        # TODO: Implémenter la recherche de vidéos
        return {"message": f"Recherche de vidéos pour {game_name} (à implémenter)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))