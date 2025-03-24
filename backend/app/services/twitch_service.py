from typing import Optional, Dict, Any, List
import httpx
from ..config import settings
from ..models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult
from ..repositories.twitch_repository import TwitchRepository
import inspect
from datetime import datetime
import logging

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwitchService:
    def __init__(self):
        self.repository = TwitchRepository()
        self.client_id = settings.TWITCH_CLIENT_ID
        self.client_secret = settings.TWITCH_CLIENT_SECRET
        self.redirect_uri = settings.TWITCH_REDIRECT_URI
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2"

    def close(self):
        """Close the service resources"""
        self.repository.close()

    async def get_auth_url(self) -> str:
        """Generate Twitch authentication URL"""
        scope = "user:read:email channel:read:stream_key"
        return f"{self.auth_url}/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}&response_type=code&scope={scope}"

    async def _get_json_safely(self, response):
        """Safely get JSON from response, handling both coroutines and non-coroutines"""
        json_method = response.json
        if inspect.iscoroutinefunction(json_method):
            return await json_method()
        return json_method()

    async def exchange_code_for_token(self, code: str) -> TwitchToken:
        """Exchange authorization code for token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                }
            )
            # Retrieve JSON safely (whether it's a coroutine or not)
            data = await self._get_json_safely(response)
            return TwitchToken(**data)

    async def get_user_info(self, token: str) -> TwitchUser:
        """Get user information from Twitch API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Client-Id": self.client_id
                }
            )
            # Retrieve JSON safely (whether it's a coroutine or not)
            data = await self._get_json_safely(response)
            if not data or "data" not in data or not data["data"]:
                raise Exception("No user data returned from Twitch API")
            
            user_data = data["data"][0]
            return TwitchUser(
                id=user_data["id"],
                login=user_data["login"],
                display_name=user_data["display_name"],
                profile_image_url=user_data["profile_image_url"],
                email=user_data.get("email", None)
            )

    async def get_user_by_login(self, login: str, token: str) -> Optional[TwitchUser]:
        """Get user information by login name from Twitch API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users",
                params={"login": login},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Client-Id": self.client_id
                }
            )
            # Retrieve JSON safely
            data = await self._get_json_safely(response)
            if not data or "data" not in data or not data["data"]:
                return None
            
            user_data = data["data"][0]
            return TwitchUser(
                id=user_data["id"],
                login=user_data["login"],
                display_name=user_data["display_name"],
                profile_image_url=user_data["profile_image_url"],
                email=user_data.get("email", None)
            )

    async def get_user_videos(self, user_id: str, token: str) -> List[Dict[str, Any]]:
        """Get user videos"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/videos",
                params={"user_id": user_id},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Client-Id": self.client_id
                }
            )
            # Retrieve JSON safely (whether it's a coroutine or not)
            result = await self._get_json_safely(response)
            return result["data"]

    async def get_stream_key(self, user_id: str, token: str) -> Dict[str, Any]:
        """Get user stream key"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/streams/key",
                params={"broadcaster_id": user_id},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Client-Id": self.client_id
                }
            )
            # Retrieve JSON safely (whether it's a coroutine or not)
            return await self._get_json_safely(response)

    async def get_game_by_name(self, game_name: str, token: str) -> Optional[TwitchGame]:
        """Search for a game by name using Twitch API"""
        logger.debug(f"Searching for game: {game_name}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/games",
                params={"name": game_name},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Client-Id": self.client_id
                }
            )
            
            data = await self._get_json_safely(response)
            
            if not data or "data" not in data or not data["data"]:
                logger.debug(f"No game found with name: {game_name}")
                return None
            
            game_data = data["data"][0]
            game = TwitchGame(
                id=game_data["id"],
                name=game_data["name"],
                box_art_url=game_data["box_art_url"]
            )
            
            # Save game data to the database
            await self.repository.save_game(game)
            
            return game

    async def get_videos_by_game_id(self, game_id: str, token: str, limit: int = 20) -> List[TwitchVideo]:
        """Get videos for a specific game ID"""
        logger.debug(f"Getting videos for game ID: {game_id}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/videos",
                params={
                    "game_id": game_id,
                    "first": limit,
                    "sort": "views",  # Sort by most popular
                    "type": "all"     # Include all video types
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "Client-Id": self.client_id
                }
            )
            
            data = await self._get_json_safely(response)
            
            if not data or "data" not in data or not data["data"]:
                logger.debug(f"No videos found for game ID: {game_id}")
                return []
            
            videos = []
            for video_data in data["data"]:
                try:
                    video = TwitchVideo(
                        id=video_data["id"],
                        user_id=video_data["user_id"],
                        user_login=video_data["user_login"],
                        user_name=video_data["user_name"],
                        title=video_data["title"],
                        description=video_data["description"],
                        created_at=video_data["created_at"],
                        published_at=video_data["published_at"],
                        url=video_data["url"],
                        thumbnail_url=video_data["thumbnail_url"],
                        viewable=video_data["viewable"],
                        view_count=video_data["view_count"],
                        language=video_data["language"],
                        type=video_data["type"],
                        duration=video_data["duration"]
                    )
                    videos.append(video)
                except Exception as e:
                    logger.error(f"Error parsing video data: {str(e)}")
            
            return videos

    async def search_videos_by_game(self, game_name: str, token: str, limit: int = 20, use_cache: bool = True) -> TwitchSearchResult:
        """
        Search for videos by game name with caching support.
        Returns a TwitchSearchResult object containing the game info and related videos.
        """
        logger.debug(f"Searching videos for game: {game_name}")
        
        # Check cache first if enabled
        if use_cache:
            cached_result = await self.repository.get_cached_game_search(game_name, limit)
            if cached_result:
                logger.debug(f"Returning cached result for game: {game_name}")
                return cached_result
        
        # If no cache or cache disabled, fetch from Twitch API
        game = await self.get_game_by_name(game_name, token)
        
        if not game:
            logger.debug(f"Game not found: {game_name}")
            # Return empty result
            return TwitchSearchResult(
                game=TwitchGame(id="0", name=game_name, box_art_url=""),
                videos=[],
                last_updated=datetime.utcnow().isoformat()
            )
        
        # Get videos for this game
        videos = await self.get_videos_by_game_id(game.id, token, limit)
        
        # Save results to cache
        await self.repository.save_game_search_results(game_name, game, videos)
        
        # Return the result
        return TwitchSearchResult(
            game=game,
            videos=videos,
            last_updated=datetime.utcnow().isoformat()
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