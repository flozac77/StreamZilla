from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from ..models.twitch import TwitchUser, TwitchToken
from ..config import settings
from datetime import datetime
from pymongo import MongoClient

class TwitchRepository:
    def __init__(self):
        """Initialize the repository with database collections."""
        # Use async client for async methods
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        self.users_collection = self.db["users"]
        self.tokens_collection = self.db["tokens"]

    def save_user_token(self, user_id: str, token_data: TwitchToken, user_info: TwitchUser) -> None:
        """Save or update user token and info in database"""
        self.tokens_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "access_token": token_data.access_token,
                "refresh_token": token_data.refresh_token,
                "user_info": user_info.model_dump()
            }},
            upsert=True
        )

    def get_user_token(self, user_id: str) -> Optional[dict]:
        """Get user token and info from database"""
        return self.tokens_collection.find_one({"user_id": user_id})

    def delete_user_token(self, user_id: str) -> None:
        """Delete user token from database"""
        self.tokens_collection.delete_one({"user_id": user_id})

    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()

    async def create_user(self, user: TwitchUser) -> TwitchUser:
        """Create a new user in the database."""
        user_dict = user.model_dump()
        # Check if user already exists
        existing_user = await self.get_user_by_id(user.id)
        
        if existing_user:
            await self.users_collection.update_one({"id": user.id}, {"$set": user_dict})
            return user
        else:
            # Otherwise, create a new user
            await self.users_collection.insert_one(user_dict)
            return user

    async def get_user_by_id(self, user_id: str) -> Optional[TwitchUser]:
        """Get a user by ID from the database."""
        user_dict = await self.users_collection.find_one({"id": user_id})
        if user_dict:
            return TwitchUser(**user_dict)
        return None

    async def update_user(self, user_id: str, **kwargs) -> Optional[TwitchUser]:
        """Update a user in the database."""
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if update_data:
            await self.users_collection.update_one({"id": user_id}, {"$set": update_data})
        return await self.get_user_by_id(user_id)

    async def delete_user(self, user_id: str) -> None:
        """Delete a user from the database."""
        await self.users_collection.delete_one({"id": user_id})

    async def save_token(self, user_id: str, token: TwitchToken) -> TwitchToken:
        """Save a token for a user in the database."""
        token_dict = token.model_dump()
        token_dict['user_id'] = user_id
        # Insert the new token
        await self.tokens_collection.update_one(
            {"user_id": user_id},
            {"$set": token_dict},
            upsert=True
        )
        return token

    async def get_token_by_user_id(self, user_id: str) -> Optional[TwitchToken]:
        """Get a token by user ID from the database."""
        token_dict = await self.tokens_collection.find_one({"user_id": user_id})
        if token_dict:
            return TwitchToken(**token_dict)
        return None

    async def update_user_token(self, user_id: str, token: TwitchToken) -> None:
        """Update user token in database"""
        token_dict = token.model_dump()
        await self.tokens_collection.update_one(
            {"user_id": user_id},
            {"$set": token_dict}
        ) 