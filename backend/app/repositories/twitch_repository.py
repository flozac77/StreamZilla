from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from ..models.twitch import TwitchGame, TwitchSearchResult, TwitchVideo
from ..config import settings
from datetime import datetime, timedelta
import logging

# Configure logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwitchRepository:
    def __init__(self):
        """Initialize the repository with database collections."""
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
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

    async def close(self):
        """Close database connection"""
        if self.client:
            await self.client.close()
            
    async def get_cached_game_search(self, game_name: str, limit: int = None) -> Optional[TwitchSearchResult]:
        """
        Get cached search results for a specific game.
        Returns None if the cache is stale (older than 2 minutes) or doesn't exist.
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
                result.videos = result.videos[:limit]
                result.total_count = len(result.videos)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving cache for game {game_name}: {str(e)}")
            return None
            
    async def save_game_search_results(self, game_name: str, game: Optional[TwitchGame], videos: List[TwitchVideo], pagination: dict) -> None:
        """
        Save search results to cache with a 2-minute TTL.
        """
        try:
            now = datetime.utcnow()
            
            # Create search result object
            search_result = TwitchSearchResult(
                game_name=game_name,
                game=game,
                videos=videos,
                total_count=len(videos),
                last_updated=now,
                pagination=pagination
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