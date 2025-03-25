from typing import Optional, Dict, Any, List
import httpx
from backend.app.config import settings
from backend.app.models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult
from backend.app.repositories.twitch_repository import TwitchRepository
import inspect
from datetime import datetime
import logging

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwitchService:
    def __init__(self):
        self.repository = TwitchRepository()
        self.client = httpx.AsyncClient()
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2"
        self.client_id = settings.TWITCH_CLIENT_ID

    async def close(self):
        """Close the service resources"""
        await self.client.aclose()
        self.repository.close()

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
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/games",
                params={"name": game_name},
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Client-Id": self.client_id
                }
            )
            response.raise_for_status()
            data = response.json()
            if not data["data"]:
                return None
            return TwitchGame(**data["data"][0])

    async def get_videos_by_game_id(self, game_id: str, auth_token: str) -> List[TwitchVideo]:
        """Récupère les vidéos pour un jeu spécifique."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/videos",
                params={"game_id": game_id},
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Client-Id": self.client_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return [TwitchVideo(**video) for video in data["data"]]

    async def search_videos_by_game(
        self,
        game_name: str,
        game: Optional[TwitchGame] = None,
        limit: int = 10,
        use_cache: bool = True
    ) -> TwitchSearchResult:
        """Search videos by game name with caching"""
        try:
            # En développement, utiliser le cache en mémoire
            if settings.ENVIRONMENT == "dev":
                cache_key = f"game_search:{game_name}:{limit}"
                if use_cache and cache_key in twitch_cache:
                    logger.debug(f"Cache hit for game search: {game_name}")
                    return twitch_cache[cache_key]

            # Si pas de cache ou pas de jeu fourni, chercher le jeu
            if not game:
                game = await self.get_game_by_name(game_name)
                if not game:
                    logger.warning(f"Game not found: {game_name}")
                    return TwitchSearchResult(
                        game_name=game_name,
                        game=None,
                        videos=[],
                        last_updated=datetime.utcnow()
                    )

            # Récupérer les vidéos
            videos = await self.get_videos_by_game_id(game.id, limit=limit)
            
            # Créer le résultat
            result = TwitchSearchResult(
                game_name=game_name,
                game=game,
                videos=videos,
                last_updated=datetime.utcnow()
            )

            # En développement, mettre en cache en mémoire
            if settings.ENVIRONMENT == "dev" and use_cache:
                twitch_cache[cache_key] = result
                logger.debug(f"Cached game search result for: {game_name}")

            return result

        except Exception as e:
            logger.error(f"Error searching videos by game: {str(e)}")
            raise

    def get_user_token(self, user_id: str) -> Optional[dict]:
        """Get user token from database"""
        return self.repository.get_user_token(user_id)

    def save_user_token(self, user_id: str, token_data: TwitchToken, user_info: TwitchUser) -> None:
        """Save user token to database"""
        self.repository.save_user_token(user_id, token_data, user_info)

    def delete_user_token(self, user_id: str) -> None:
        """Delete user token from database"""
        self.repository.delete_user_token(user_id) 