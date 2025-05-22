import asyncio
import logging
from datetime import datetime, timedelta
from fastapi_cache import FastAPICache

logger = logging.getLogger(__name__)

class CacheScheduler:
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self.is_running = False
        self._task = None
        
    async def start(self):
        """Démarre le scheduler"""
        if self.is_running:
            return
            
        self.is_running = True
        self._task = asyncio.create_task(self._run())
        logger.info("Scheduler démarré")
        
    async def stop(self):
        """Arrête le scheduler"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler arrêté")
        
    async def _run(self):
        """Boucle principale du scheduler"""
        while self.is_running:
            try:
                # Nettoyage du cache
                # await FastAPICache.clear()
                # logger.info(f"Cache nettoyé à {datetime.now()}")
                # FastAPICache is initialized but not actively used for route caching or data storage.
                # The primary caching (Twitch game search) is handled by TwitchRepository using MongoDB's TTL.
                # Therefore, clearing FastAPICache here is currently a no-op or clears an empty cache.
                # Kept the scheduler structure for potential future tasks.
                logger.debug(f"CacheScheduler running at {datetime.now()}, FastAPICache.clear() is commented out.")
                
                # Attendre jusqu'au prochain cycle
                await asyncio.sleep(self.cache_ttl)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans le scheduler: {e}")
                await asyncio.sleep(60)  # Attendre 1 minute en cas d'erreur
            
    # async def _update_cache(self):
    #     """Exemple de tâche périodique pour mettre à jour le cache"""
    #     pass