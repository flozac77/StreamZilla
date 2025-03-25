from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from ..models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult
from ..config import settings
from datetime import datetime, timedelta
from pymongo import MongoClient
import logging

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwitchRepository:
    def __init__(self):
        """Initialize the repository with database collections."""
        # Use async client for async methods
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        self.users_collection = self.db["users"]
        self.tokens_collection = self.db["tokens"]
        self.games_collection = self.db["games"]
        self.search_cache_collection = self.db["search_cache"]
        
        # Create TTL index for search cache (expire after 2 minutes)
        try:
            self.search_cache_collection.create_index(
                "created_at", 
                expireAfterSeconds=120  # 2 minutes
            )
            logger.debug("TTL index created for search_cache collection")
        except Exception as e:
            logger.error(f"Error creating TTL index: {str(e)}")

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
        
    async def get_cached_game_search(self, game_name: str, limit: int = None) -> Optional[TwitchSearchResult]:
        """
        Get cached search results for a specific game.
        Returns None if the cache is stale (older than 2 minutes) or doesn't exist.
        
        If limit is provided, it will limit the number of videos returned in the result.
        """
        try:
            # Find the most recent cache for this game name
            cache_result = await self.search_cache_collection.find_one(
                {"game_name": game_name.lower()},
                sort=[("created_at", -1)]  # Sort by most recent
            )
            
            if not cache_result:
                logger.debug(f"No cache found for game: {game_name}")
                return None
                
            # Check if the cache is still valid (less than 2 minutes old)
            created_at = cache_result.get("created_at")
            if not created_at:
                return None
                
            cache_age = datetime.utcnow() - created_at
            if cache_age > timedelta(minutes=2):
                logger.debug(f"Cache for game {game_name} is stale ({cache_age.total_seconds()} seconds old)")
                return None
                
            logger.debug(f"Using cache for game {game_name} ({cache_age.total_seconds()} seconds old)")
            
            # Apply limit if specified
            result = TwitchSearchResult(**cache_result["result"])
            if limit is not None and limit > 0 and len(result.videos) > limit:
                # Create a new result with limited videos
                limited_result = TwitchSearchResult(
                    game=result.game,
                    videos=result.videos[:limit],
                    last_updated=result.last_updated
                )
                return limited_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving cache for game {game_name}: {str(e)}")
            return None
            
    async def save_game_search_results(self, game_name: str, game: TwitchGame, videos: List[TwitchVideo]) -> None:
        """
        Save search results to cache with a 2-minute TTL.
        """
        try:
            now = datetime.utcnow()
            
            # Create search result object
            search_result = TwitchSearchResult(
                game=game,
                videos=videos,
                last_updated=now.isoformat()
            )
            
            # Save to cache collection with current timestamp
            await self.search_cache_collection.insert_one({
                "game_name": game_name.lower(),
                "result": search_result.model_dump(),
                "created_at": now
            })
            
            logger.debug(f"Saved search results for game: {game_name}")
            
        except Exception as e:
            logger.error(f"Error saving search results for game {game_name}: {str(e)}")
            
    async def save_game(self, game: TwitchGame) -> None:
        """Save game information to database"""
        try:
            game_dict = game.model_dump()
            await self.games_collection.update_one(
                {"id": game.id},
                {"$set": game_dict},
                upsert=True
            )
            logger.debug(f"Saved game: {game.name}")
        except Exception as e:
            logger.error(f"Error saving game {game.name}: {str(e)}") 