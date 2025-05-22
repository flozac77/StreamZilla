from typing import Optional, List, Tuple
import httpx
from datetime import datetime, timedelta
import logging
from cachetools import TTLCache
from fastapi import HTTPException
from pydantic import ValidationError

from backend.app.config import settings
from backend.app.models.twitch import TwitchUser, TwitchToken, TwitchVideo, TwitchGame, TwitchSearchResult
from backend.app.repositories.token_repository import TokenRepository
from backend.app.repositories.twitch_repository import TwitchRepository
from backend.app.services.twitch.auth import TwitchAuthService

# Configure logger
logger = logging.getLogger(__name__)

class TwitchService:
    def __init__(self):
        """Initialize the Twitch service with necessary components."""
        self.client = httpx.AsyncClient()
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2"
        self.client_id = settings.TWITCH_CLIENT_ID
        self.auth_service = None
        self.twitch_repository = TwitchRepository()
        
        # Cache en mémoire pour les données fréquemment accédées
        self.memory_cache = TTLCache(
            maxsize=settings.CACHE_MAX_SIZE,
            ttl=settings.CACHE_TTL
        )

    async def _get_auth_service(self) -> TwitchAuthService:
        """Lazy initialization of auth service."""
        if not self.auth_service:
            from backend.app.dependencies import get_db
            db = await get_db()
            token_repository = TokenRepository(db)
            self.auth_service = TwitchAuthService(token_repository)
        return self.auth_service

    async def close(self):
        """Close all service resources."""
        await self.client.aclose()
        if self.auth_service:
            await self.auth_service.close()
        await self.twitch_repository.close()

    async def get_auth_url(self) -> str:
        """Generate Twitch OAuth URL"""
        return f"{self.auth_url}/authorize?client_id={settings.TWITCH_CLIENT_ID}&redirect_uri={settings.TWITCH_REDIRECT_URI}&response_type=code&scope=user:read:email"

    async def exchange_code_for_token(self, code: str) -> TwitchToken:
        """Exchange authorization code for access token"""
        logger.debug("Début exchange_code_for_token avec code: %s", code)
        data = {
            "client_id": settings.TWITCH_CLIENT_ID,
            "client_secret": settings.TWITCH_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.TWITCH_REDIRECT_URI
        }
        logger.info("Données de requête token: %s", {k: '***' if k in ['client_secret', 'code'] else v for k, v in data.items()})
        
        async with httpx.AsyncClient() as client:
           logger.debug("Envoi requête token à Twitch...")
           response = await client.post(f"{self.auth_url}/token", data=data)
           logger.debug("Réponse Twitch reçue, status: %d", response.status_code)
           
           if response.status_code != 200:
               logger.error("Twitch token error %s: %s", response.status_code, response.text)
               raise HTTPException(400, detail=f"Twitch token error: {response.json()}")
           
           # Récupérer la réponse et calculer expires_at
           token_data = response.json()
           logger.debug("Twitch token raw: %s", {k: '***' if k in ['access_token', 'refresh_token'] else v for k, v in token_data.items()})
           
           if "expires_in" in token_data:
               token_data["expires_at"] = (datetime.utcnow() + timedelta(seconds=token_data["expires_in"])).isoformat()
               logger.debug("Token expires_at calculé: %s", token_data["expires_at"])
           else:
               logger.error("Champ expires_in manquant dans la réponse Twitch")
               raise HTTPException(500, detail="Erreur: expires_in manquant dans la réponse Twitch")
               
           try:
               logger.debug("Tentative de création du TwitchToken...")
               token = TwitchToken(**token_data)
               logger.debug("TwitchToken créé avec succès")
               return token
           except ValidationError as e:
               logger.error("Erreur de validation TwitchToken: %s", e)
               raise HTTPException(500, detail=f"Erreur interne sur le token Twitch: {str(e)}")

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

    async def _get_headers(self) -> dict:
        """Génère les headers nécessaires pour les appels API Twitch."""
        if not self.auth_service:
            self.auth_service = await self._get_auth_service()
        token = await self.auth_service.get_valid_token()
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token.access_token}"
        }

    async def search_videos_by_game(
        self,
        game_name: str,
        limit: int = 100,
        cursor: Optional[str] = None,
        use_cache: bool = False
    ) -> TwitchSearchResult:
        """
        Recherche des vidéos sur Twitch avec gestion du cache.
        
        Args:
            game_name: Nom du jeu à rechercher
            limit: Nombre maximum de résultats
            cursor: Curseur pour la pagination
            use_cache: Utiliser le cache ou non
            
        Returns:
            TwitchSearchResult: Résultats de la recherche
        """
        try:
            # Vérifier le cache si activé
            if use_cache and not cursor:
                cached_result = await self.twitch_repository.get_cached_game_search(
                    game_name=game_name,
                    limit=limit
                )
                if cached_result:
                    logger.info(f"Cache hit for game: {game_name}")
                    return cached_result

            # Si pas de cache ou cache expiré, faire l'appel API
            logger.info(f"Cache miss for game: {game_name}, fetching from API")
            headers = await self._get_headers()
            
            # 1. Rechercher le jeu
            game = await self._find_game(game_name, headers)
            if not game:
                logger.warning(f"No game found for: {game_name}")
                return self._empty_result(game_name)

            # 2. Récupérer les streams et vidéos
            videos, pagination = await self._fetch_videos(
                game_id=game.id,
                limit=limit,
                cursor=cursor,
                headers=headers
            )

            # Créer le résultat
            result = TwitchSearchResult(
                game_name=game_name,
                game=game,
                videos=videos,
                total_count=len(videos),
                last_updated=datetime.utcnow(),
                pagination=pagination
            )

            # Sauvegarder dans le cache si pas de cursor
            if use_cache and not cursor:
                await self.twitch_repository.save_game_search_results(
                    game_name=game_name,
                    result=result
                )

            return result

        except Exception as e:
            logger.error(f"Error in search: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error searching videos: {str(e)}"
            )

    _GAME_NOT_FOUND_MARKER = object() # Special marker for games not found

    async def _find_game(self, game_name: str, headers: dict) -> Optional[TwitchGame]:
        """Recherche un jeu sur Twitch."""
        cache_key = f"game_{game_name}"
        cached_game = self.memory_cache.get(cache_key)

        if cached_game is not None:
            if cached_game is self._GAME_NOT_FOUND_MARKER:
                logger.debug(f"Cache hit for not found game: {game_name}")
                return None
            logger.debug(f"Cache hit for game: {game_name}")
            return cached_game

        try:
            logger.warning(f"[Twitch API Request] GET /search/categories - Params: query={game_name}, first=1")
            # logger.warning(f"[Twitch API Request] Headers: {headers}") # Headers can contain sensitive token
            
            response = await self.client.get(
                f"{self.base_url}/search/categories",
                params={"query": game_name, "first": 1},
                headers=headers
            )
            
            logger.warning(f"[Twitch API Response] Status: {response.status_code}")
            # logger.warning(f"[Twitch API Response] Body: {response.json()}") # Can be large
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("data"):
                logger.warning(f"[Twitch API] No game found for query: {game_name}")
                # Cache "not found" for a shorter period
                self.memory_cache.set(cache_key, self._GAME_NOT_FOUND_MARKER, ttl=settings.CACHE_TTL / 10)
                return None
                
            game = TwitchGame(**data["data"][0])
            await self.twitch_repository.save_game(game)
            self.memory_cache[cache_key] = game # Use default TTL from __init__
            logger.debug(f"Game {game_name} cached.")
            return game
            
        except Exception as e:
            logger.error(f"[Twitch API Error] Error finding game: {str(e)}")
            # Do not cache errors to allow retries
            return None

    async def _fetch_videos(
        self,
        game_id: str,
        limit: int,
        cursor: Optional[str],
        headers: dict
    ) -> Tuple[List[TwitchVideo], dict]:
        """Récupère les streams et vidéos pour un jeu."""
        all_videos = []
        seen_ids = set()
        pagination = {"cursor": None}

        # 1. Récupérer les streams en direct
        try:
            stream_params = {"game_id": game_id, "first": min(100, limit)}
            if cursor:
                stream_params["after"] = cursor
            
            streams_cache_key = f"streams_{game_id}_{stream_params.get('first', 100)}_{stream_params.get('after', '')}"
            cached_stream_data = self.memory_cache.get(streams_cache_key)

            if cached_stream_data:
                logger.debug(f"Cache hit for streams: {streams_cache_key}")
                stream_data = cached_stream_data
            else:
                logger.info(f"[Twitch API Request] GET /streams - Params: {stream_params}")
                # logger.info(f"[Twitch API Request] Headers: {headers}")

                stream_response = await self.client.get(
                    f"{self.base_url}/streams",
                    params=stream_params,
                    headers=headers
                )
                
                logger.info(f"[Twitch API Response] Status: {stream_response.status_code}")
                # logger.info(f"[Twitch API Response] Body: {stream_response.json()}")
            
                stream_response.raise_for_status()
                stream_data = stream_response.json()
                self.memory_cache[streams_cache_key] = stream_data
                logger.debug(f"Streams data cached: {streams_cache_key}")

            for stream in stream_data.get("data", []):
                if stream["id"] not in seen_ids and len(all_videos) < limit:
                    video = TwitchVideo(
                        id=stream["id"],
                        title=stream["title"],
                        thumbnail_url=stream["thumbnail_url"],
                        user_name=stream["user_name"],
                        game_id=stream["game_id"],
                        type="live",
                        view_count=stream["viewer_count"],
                        language=stream["language"],
                        created_at=stream["started_at"],
                        url=f"https://www.twitch.tv/{stream.get('user_login', stream['user_name']).lower()}",
                        duration="live"
                    )
                    all_videos.append(video)
                    seen_ids.add(stream["id"])

            pagination = {"cursor": stream_data.get("pagination", {}).get("cursor")}

        except Exception as e:
            logger.error(f"[Twitch API Error] Error fetching streams: {str(e)}")

        # 2. Si on n'a pas atteint la limite, ajouter des vidéos archivées
        if len(all_videos) < limit:
            try:
                remaining_limit = limit - len(all_videos)
                video_params = {
                    "game_id": game_id,
                    "first": remaining_limit,
                    "type": "archive"
                    # cursor for videos is not used in the same way as streams, 
                    # and this part fetches archives if streams are less than limit,
                    # so a direct pagination cursor from input might not be applicable here.
                    # If pagination for videos was needed, it would require a separate cursor.
                }
                
                videos_cache_key = f"videos_{game_id}_{video_params.get('first', 20)}_{video_params.get('type', 'archive')}"
                cached_video_data = self.memory_cache.get(videos_cache_key)

                if cached_video_data:
                    logger.debug(f"Cache hit for videos: {videos_cache_key}")
                    video_data = cached_video_data
                else:
                    logger.info(f"[Twitch API Request] GET /videos - Params: {video_params}")
                    # logger.info(f"[Twitch API Request] Headers: {headers}")

                    video_response = await self.client.get(
                        f"{self.base_url}/videos",
                        params=video_params,
                        headers=headers
                    )
                    
                    logger.info(f"[Twitch API Response] Status: {video_response.status_code}")
                    # logger.info(f"[Twitch API Response] Body: {video_response.json()}")
                    
                    video_response.raise_for_status()
                    video_data = video_response.json()
                    self.memory_cache[videos_cache_key] = video_data
                    logger.debug(f"Videos data cached: {videos_cache_key}")
                
                for video in video_data.get("data", []):
                    if video["id"] not in seen_ids and len(all_videos) < limit:
                        video_obj = TwitchVideo(
                            id=video["id"],
                            title=video["title"],
                            thumbnail_url=video["thumbnail_url"],
                            user_name=video["user_name"],
                            game_id=game_id,
                            type="archive",
                            view_count=video.get("view_count"),
                            language=video.get("language", ""),
                            created_at=video.get("created_at", ""),
                            url=video.get("url", ""),
                            duration=video.get("duration", "")
                        )
                        all_videos.append(video_obj)
                        seen_ids.add(video["id"])

            except Exception as e:
                logger.error(f"[Twitch API Error] Error fetching archived videos: {str(e)}")

        return all_videos, pagination

    def _empty_result(self, game_name: str) -> TwitchSearchResult:
        """Crée un résultat vide."""
        return TwitchSearchResult(
            game_name=game_name,
            game=None,
            videos=[],
            total_count=0,
            last_updated=datetime.utcnow(),
            pagination={"cursor": None}
        ) 