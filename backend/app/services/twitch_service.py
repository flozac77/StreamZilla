from typing import Optional, List
import httpx
from datetime import datetime
import logging
from cachetools import TTLCache

from backend.app.config import settings
from backend.app.models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult
from backend.app.repositories.token_repository import TokenRepository
from backend.app.services.twitch.auth import TwitchAuthService

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwitchService:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2"
        self.client_id = settings.TWITCH_CLIENT_ID
        self.auth_service = None
        # Cache en mémoire pour le dev
        self.cache = TTLCache(maxsize=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL)

    async def _get_auth_service(self) -> TwitchAuthService:
        """
        Lazy initialization of auth service to avoid circular imports
        """
        if not self.auth_service:
            from backend.app.dependencies import get_db
            db = await get_db()
            token_repository = TokenRepository(db)
            self.auth_service = TwitchAuthService(token_repository)
        return self.auth_service

    async def close(self):
        """Close the service resources"""
        await self.client.aclose()
        if self.auth_service:
            await self.auth_service.close()

    async def get_auth_url(self) -> str:
        """Generate Twitch OAuth URL"""
        return f"{self.auth_url}/authorize?client_id={settings.TWITCH_CLIENT_ID}&redirect_uri={settings.TWITCH_REDIRECT_URI}&response_type=code&scope=user:read:email"

    async def exchange_code_for_token(self, code: str) -> TwitchToken:
        """Exchange authorization code for access token"""
        data = {
            "client_id": settings.TWITCH_CLIENT_ID,
            "client_secret": settings.TWITCH_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.TWITCH_REDIRECT_URI
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.auth_url}/token", data=data)
            response.raise_for_status()
            return TwitchToken(**response.json())

    async def get_user_info(self, token: str) -> TwitchUser:
        """Get current user information"""
        headers = {
            "Client-ID": settings.TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {token}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/users", headers=headers)
            response.raise_for_status()
            data = response.json()["data"][0]
            return TwitchUser(**data)

    async def search_videos_by_game(
        self,
        game_name: str,
        limit: int = 100,
        cursor: Optional[str] = None,
        use_cache: bool = True
    ) -> TwitchSearchResult:
        """
        Recherche des vidéos sur Twitch avec une meilleure gestion de la pagination
        """
        try:
            logger.debug(f"Starting search for: {game_name}")
            auth_service = await self._get_auth_service()
            token = await auth_service.get_valid_token()
            
            headers = {
                "Client-Id": self.client_id,
                "Authorization": f"Bearer {token.access_token}"
            }
            
            # 1. Chercher l'ID du jeu
            game_response = await self.client.get(
                f"{self.base_url}/search/categories",
                params={"query": game_name, "first": 1},
                headers=headers
            )
            game_data = game_response.json()
            logger.debug(f"Game search response: {game_data}")
            
            if not game_data.get("data"):
                logger.warning(f"No game found for query: {game_name}")
                return self._empty_result(game_name)
            
            game = TwitchGame(**game_data["data"][0])
            logger.info(f"Found game: {game.name} (ID: {game.id})")
            
            all_videos = []
            seen_ids = set()
            
            # 2. Chercher les streams en direct
            stream_params = {
                "game_id": game.id,
                "first": 100
            }
            if cursor:
                stream_params["after"] = cursor
            
            stream_response = await self.client.get(
                f"{self.base_url}/streams",
                params=stream_params,
                headers=headers
            )
            stream_data = stream_response.json()
            logger.debug(f"Stream response: {stream_data}")
            
            # Traiter les streams
            for stream in stream_data.get("data", []):
                if stream["id"] not in seen_ids and len(all_videos) < limit:
                    try:
                        video = TwitchVideo(
                            id=str(stream["id"]),
                            user_name=stream["user_name"],
                            title=stream["title"],
                            url=f"https://twitch.tv/{stream['user_login']}",
                            view_count=stream["viewer_count"],
                            duration="LIVE",
                            created_at=stream["started_at"],
                            language=stream["language"],
                            thumbnail_url=stream["thumbnail_url"],
                            game_id=stream["game_id"],
                            game_name=stream["game_name"],
                            type="live"
                        )
                        all_videos.append(video)
                        seen_ids.add(stream["id"])
                    except Exception as e:
                        logger.warning(f"Failed to parse stream: {e}")
                        continue
            
            # Si on n'a pas atteint la limite avec les streams, chercher les vidéos archivées
            remaining_limit = limit - len(all_videos)
            if remaining_limit > 0:
                video_params = {
                    "game_id": game.id,
                    "first": remaining_limit,
                    "sort": "views",
                    "type": "all"
                }
                if cursor and not stream_data.get("data"):
                    video_params["after"] = cursor
                
                video_response = await self.client.get(
                    f"{self.base_url}/videos",
                    params=video_params,
                    headers=headers
                )
                video_data = video_response.json()
                logger.debug(f"Video response: {video_data}")
                
                # Traiter les vidéos
                for video in video_data.get("data", []):
                    if video["id"] not in seen_ids and len(all_videos) < limit:
                        try:
                            video["type"] = "archive"
                            video_obj = TwitchVideo(**video)
                            all_videos.append(video_obj)
                            seen_ids.add(video["id"])
                        except Exception as e:
                            logger.warning(f"Failed to parse video: {e}")
                            continue
            
            # Gérer la pagination
            pagination = {}
            if len(all_videos) >= limit:
                if stream_data.get("data"):
                    pagination = stream_data.get("pagination", {})
                else:
                    pagination = video_data.get("pagination", {})
            
            # Trier les résultats
            all_videos.sort(key=lambda v: (
                v.type == "live",
                v.view_count or 0
            ), reverse=True)
            
            total_found = len(all_videos)
            logger.debug(f"Found {total_found} videos total")
            
            return TwitchSearchResult(
                game_name=game_name,
                game=game,
                videos=all_videos,
                total_count=total_found,
                last_updated=datetime.utcnow(),
                pagination=pagination
            )

        except Exception as e:
            logger.error(f"Error in search: {str(e)}", exc_info=True)
            return self._empty_result(game_name)

    def _empty_result(self, game_name: str) -> TwitchSearchResult:
        """Helper pour créer un résultat vide"""
        return TwitchSearchResult(
            game_name=game_name,
            game=None,
            videos=[],
            total_count=0,
            last_updated=datetime.utcnow(),
            pagination={"cursor": None}
        ) 