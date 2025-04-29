import platform
import logging
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from backend.app.config import settings

logger = logging.getLogger(__name__)

async def setup_cache():
    """Configure le cache en fonction de l'OS"""
    cache_prefix = "dbTwitch-cache"
    
    # Détection de l'OS
    is_windows = platform.system().lower() == "windows"
    
    if is_windows:
        logger.info("Environnement Windows : utilisation du cache mémoire")
        FastAPICache.init(InMemoryBackend(), prefix=cache_prefix)
    else:
        # Import conditionnel pour éviter les erreurs sur Windows
        try:
            from fastapi_cache.backends.redis import RedisBackend
            import redis.asyncio as redis
            
            if settings.REDIS_URL:
                logger.info("Environnement non-Windows : utilisation de Redis")
                redis_client = redis.from_url(settings.REDIS_URL)
                FastAPICache.init(RedisBackend(redis_client), prefix=cache_prefix)
            else:
                logger.info("Redis non configuré, utilisation du cache mémoire")
                FastAPICache.init(InMemoryBackend(), prefix=cache_prefix)
        except ImportError:
            logger.warning("Redis non disponible, fallback sur cache mémoire")
            FastAPICache.init(InMemoryBackend(), prefix=cache_prefix) 