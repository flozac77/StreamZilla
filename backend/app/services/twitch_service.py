from typing import Optional, Dict, Any, List
import httpx
from ..config import settings
from ..models.twitch import TwitchUser, TwitchToken
from ..repositories.twitch_repository import TwitchRepository
import inspect
from datetime import datetime

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

    def get_user_token(self, user_id: str) -> Optional[dict]:
        """Get user token from database"""
        return self.repository.get_user_token(user_id)

    def save_user_token(self, user_id: str, token_data: TwitchToken, user_info: TwitchUser) -> None:
        """Save user token to database"""
        self.repository.save_user_token(user_id, token_data, user_info)

    def delete_user_token(self, user_id: str) -> None:
        """Delete user token from database"""
        self.repository.delete_user_token(user_id) 