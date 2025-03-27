from cachetools import TTLCache
from datetime import datetime

class Cache:
    def __init__(self):
        # Cache principal pour les données avec TTL de 5 minutes (300 secondes)
        self._cache = TTLCache(maxsize=100, ttl=300)
        # Cache pour les timestamps de dernière mise à jour
        self._last_updated = {}

    def get(self, key: str):
        """Récupère une valeur du cache"""
        return self._cache.get(key)

    def set(self, key: str, value: any, ttl: int = 300):
        """Stocke une valeur dans le cache"""
        self._cache[key] = value
        self.update_last_updated(key)

    def get_last_updated(self, key: str) -> str:
        """Récupère le timestamp de dernière mise à jour pour une clé"""
        return self._last_updated.get(key, datetime.now().isoformat())

    def update_last_updated(self, key: str):
        """Met à jour le timestamp de dernière mise à jour"""
        self._last_updated[key] = datetime.now().isoformat()

    def clear(self):
        """Vide le cache"""
        self._cache.clear()
        self._last_updated.clear()

# Instance singleton du cache
cache = Cache() 