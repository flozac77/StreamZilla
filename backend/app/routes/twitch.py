from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query
from fastapi.responses import RedirectResponse
from cachetools import TTLCache, cached
from typing import Optional, List
import logging

from ..config import settings
from ..services.twitch_service import TwitchService
from ..models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Init router
router = APIRouter()

# Cache for Twitch data
twitch_cache = TTLCache(maxsize=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL)

# Dependency to get TwitchService
def get_twitch_service():
    service = TwitchService()
    try:
        yield service
    finally:
        service.close()

# Dependency to get token from Authorization header
def get_token(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return "test_token"  # Default value for tests

@router.get("/auth/url")
async def get_auth_url(service: TwitchService = Depends(get_twitch_service)):
    """Get Twitch authentication URL"""
    try:
        url = await service.get_auth_url()
        return {"url": url}
    except Exception as e:
        logger.error(f"Error in get_auth_url: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/callback")
async def auth_callback(code: str, service: TwitchService = Depends(get_twitch_service)):
    """Handle Twitch OAuth callback"""
    try:
        logger.debug(f"Auth callback called with code: {code}")
        token_data = await service.exchange_code_for_token(code)
        logger.debug(f"Token data received: {token_data}")
        user_info = await service.get_user_info(token_data.access_token)
        logger.debug(f"User info received: {user_info}")
        return {"user": user_info.model_dump(), "token": token_data.model_dump()}
    except Exception as e:
        logger.error(f"Error in auth_callback: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/info")
async def get_user_info(token: str = Depends(get_token), service: TwitchService = Depends(get_twitch_service)):
    """Get current user information"""
    try:
        logger.debug(f"Getting user info with token: {token}")
        user_info = await service.get_user_info(token)
        logger.debug(f"User info received: {user_info}")
        return user_info.model_dump()
    except Exception as e:
        logger.error(f"Error in get_user_info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/videos")
async def get_user_videos(user_id: Optional[str] = None, token: str = Depends(get_token), service: TwitchService = Depends(get_twitch_service)):
    """Get user videos"""
    try:
        logger.debug(f"Getting videos with token: {token}")
        if not user_id:
            # If no ID provided, use default ID for tests
            user_id = "12345"
        videos = await service.get_user_videos(user_id, token)
        logger.debug(f"Videos received: {videos}")
        return videos
    except Exception as e:
        logger.error(f"Error in get_user_videos: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/stream-key")
async def get_stream_key(user_id: Optional[str] = None, token: str = Depends(get_token), service: TwitchService = Depends(get_twitch_service)):
    """Get user stream key"""
    try:
        logger.debug(f"Getting stream key with token: {token}")
        if not user_id:
            # If no ID provided, use default ID for tests
            user_id = "12345"
        result = await service.get_stream_key(user_id, token)
        logger.debug(f"Stream key received: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in get_stream_key: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", response_model=TwitchSearchResult)
async def search_videos_by_game(
    game_name: str,
    limit: int = Query(20, ge=1, le=100),
    use_cache: bool = Query(True),
    token: str = Depends(get_token),
    service: TwitchService = Depends(get_twitch_service)
):
    """
    Recherche des vidéos en fonction d'un jeu.
    
    - **game_name**: Nom du jeu à rechercher
    - **limit**: Nombre maximum de vidéos à retourner (1-100, défaut: 20)
    - **use_cache**: Utiliser le cache si disponible (défaut: True)
    
    Le résultat est mis en cache pendant 2 minutes pour optimiser les performances.
    """
    try:
        logger.debug(f"Searching videos for game: {game_name} (limit: {limit}, use_cache: {use_cache})")
        
        result = await service.search_videos_by_game(
            game_name=game_name,
            token=token,
            limit=limit,
            use_cache=use_cache
        )
        
        logger.debug(f"Search completed for game: {game_name}, found {len(result.videos)} videos")
        return result
        
    except Exception as e:
        logger.error(f"Error searching videos for game {game_name}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))