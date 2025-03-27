from typing import Optional, Dict, Any, List
import httpx
from backend.app.config import settings
from backend.app.models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult
from backend.app.repositories.token_repository import TokenRepository
from backend.app.services.twitch.auth import TwitchAuthService
import inspect
from datetime import datetime
import logging
from functools import lru_cache
from cachetools import TTLCache

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
            db = await get_db()  # Await la coroutine get_db()
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

    async def _get_json_safely(self, response):
        """Safely get JSON from response, handling both coroutines and non-coroutines"""
        json_method = response.json
        if inspect.iscoroutinefunction(json_method):
            return await json_method()
        return json_method()

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

    async def get_user_videos(self, user_id: str, auth_token: str) -> List[TwitchVideo]:
        """Récupère les vidéos d'un utilisateur Twitch."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/videos",
                params={"user_id": user_id},
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Client-Id": self.client_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return [TwitchVideo(**video) for video in data["data"]]

    async def get_stream_key(self, user_id: str, auth_token: str) -> str:
        """Récupère la clé de stream d'un utilisateur Twitch."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/streams/key",
                params={"broadcaster_id": user_id},
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Client-Id": self.client_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["stream_key"]

    async def get_game_by_name(self, game_name: str, auth_token: str) -> Optional[TwitchGame]:
        """Recherche un jeu par son nom."""
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {auth_token}"
        }
        
        response = await self.client.get(
            f"{self.base_url}/games",
            params={"name": game_name},
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        if not data["data"]:
            return None
        return TwitchGame(**data["data"][0])

    async def get_videos_by_game_id(self, game_id: str, auth_token: str) -> List[TwitchVideo]:
        """Récupère les vidéos pour un jeu spécifique."""
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {auth_token}"
        }
        
        response = await self.client.get(
            f"{self.base_url}/videos",
            params={"game_id": game_id},
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return [TwitchVideo(**video) for video in data["data"]]

    async def search_videos_by_game(
        self,
        game_name: str,
        game: Optional[TwitchGame] = None,
        limit: int = 100,
        offset: int = 0,
        use_cache: bool = True
    ) -> TwitchSearchResult:
        """Search videos by game name with caching"""
        try:
            # Obtenir le service d'auth et un token valide
            auth_service = await self._get_auth_service()
            token = await auth_service.get_valid_token()

            # Si pas de cache ou pas de jeu fourni, chercher le jeu
            if not game:
                game = await self.get_game_by_name(game_name, token.access_token)
                if not game:
                    logger.warning(f"Game not found: {game_name}")
                    return TwitchSearchResult(
                        game_name=game_name,
                        game=None,
                        videos=[],
                        total_count=0,
                        last_updated=datetime.utcnow()
                    )

            # Récupérer les vidéos
            videos = await self.get_videos_by_game_id(game.id, token.access_token)
            total_count = len(videos)
            
            # Appliquer la pagination
            paginated_videos = videos[offset:offset + limit]
            
            # Créer le résultat
            result = TwitchSearchResult(
                game_name=game_name,
                game=game,
                videos=paginated_videos,
                total_count=total_count,
                last_updated=datetime.utcnow()
            )

            return result

        except Exception as e:
            logger.error(f"Error searching videos by game: {str(e)}")
            # Retourner un résultat vide mais valide
            return TwitchSearchResult(
                game_name=game_name,
                game=None,
                videos=[],
                total_count=0,
                last_updated=datetime.utcnow()
            )

    def get_user_token(self, user_id: str) -> Optional[dict]:
        """Get user token from database"""
        return self.repository.get_user_token(user_id)

    def save_user_token(self, user_id: str, token_data: TwitchToken, user_info: TwitchUser) -> None:
        """Save user token to database"""
        self.repository.save_user_token(user_id, token_data, user_info)

    def delete_user_token(self, user_id: str) -> None:
        """Delete user token from database"""
        self.repository.delete_user_token(user_id) 