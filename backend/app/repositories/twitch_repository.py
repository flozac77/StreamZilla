from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
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
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Ensure all required indexes exist."""
        try:
            # Index pour le cache de recherche (TTL 2 minutes)
            self.search_cache_collection.create_index(
                "created_at", 
                expireAfterSeconds=120
            )
            # Index composé pour la recherche rapide par nom de jeu et date
            self.search_cache_collection.create_index([
                ("game_name", 1),
                ("created_at", -1)
            ])
            # Index pour les jeux
            self.games_collection.create_index("name")
            logger.info("Indexes created successfully")
        except PyMongoError as e:
            logger.error(f"Error creating indexes: {str(e)}")

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()

    async def get_cached_game_search(self, game_name: str, limit: int = None) -> Optional[TwitchSearchResult]:
        """
        Get cached search results for a specific game.
        Returns None if the cache is stale or doesn't exist.
        """
        try:
            cache_result = await self.search_cache_collection.find_one(
                {"game_name": game_name.lower()},
                sort=[("created_at", -1)]
            )
            
            if not cache_result:
                logger.debug(f"No cache found for game: {game_name}")
                return None
                
            created_at = cache_result.get("created_at")
            if not created_at:
                logger.warning(f"Invalid cache entry for game {game_name}: missing created_at")
                await self.invalidate_game_cache(game_name)
                return None
                
            cache_age = datetime.utcnow() - created_at
            if cache_age > timedelta(minutes=2):
                logger.debug(f"Cache for game {game_name} is stale ({cache_age.total_seconds()}s old)")
                await self.invalidate_game_cache(game_name)
                return None
                
            logger.info(f"Cache hit for game {game_name} ({cache_age.total_seconds()}s old)")
            
            result = TwitchSearchResult(**cache_result["result"])
            if limit and limit > 0:
                result.videos = result.videos[:limit]
                result.total_count = len(result.videos)
            
            return result
            
        except PyMongoError as e:
            logger.error(f"Database error retrieving cache for {game_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving cache for {game_name}: {str(e)}")
            return None

    async def save_game_search_results(self, game_name: str, result: TwitchSearchResult) -> bool:
        """
        Save search results to cache.
        Returns True if successful, False otherwise.
        """
        try:
            # Invalider l'ancien cache d'abord
            await self.invalidate_game_cache(game_name)
            
            # Sauvegarder les nouveaux résultats
            await self.search_cache_collection.insert_one({
                "game_name": game_name.lower(),
                "result": result.model_dump(),
                "created_at": datetime.utcnow()
            })
            
            logger.info(f"Cache updated for game: {game_name}")
            return True
            
        except PyMongoError as e:
            logger.error(f"Database error saving cache for {game_name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving cache for {game_name}: {str(e)}")
            return False

    async def invalidate_game_cache(self, game_name: str) -> bool:
        """
        Invalider explicitement le cache pour un jeu donné.
        Returns True if successful, False otherwise.
        """
        try:
            result = await self.search_cache_collection.delete_many({
                "game_name": game_name.lower()
            })
            logger.info(f"Invalidated {result.deleted_count} cache entries for game: {game_name}")
            return True
        except PyMongoError as e:
            logger.error(f"Error invalidating cache for {game_name}: {str(e)}")
            return False

    async def clear_all_cache(self) -> bool:
        """
        Vider tout le cache.
        Returns True if successful, False otherwise.
        """
        try:
            result = await self.search_cache_collection.delete_many({})
            logger.info(f"Cleared {result.deleted_count} cache entries")
            return True
        except PyMongoError as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    async def save_game(self, game: TwitchGame) -> bool:
        """
        Save game information to database.
        Returns True if successful, False otherwise.
        """
        try:
            result = await self.games_collection.update_one(
                {"id": game.id},
                {"$set": game.model_dump()},
                upsert=True
            )
            logger.info(f"Game saved/updated: {game.name}")
            return True
        except PyMongoError as e:
            logger.error(f"Error saving game {game.name}: {str(e)}")
            return False 