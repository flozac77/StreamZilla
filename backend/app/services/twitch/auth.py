import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx
from fastapi import HTTPException
from cachetools import TTLCache

from backend.app.config.twitch import get_twitch_settings
from backend.app.models.twitch import TwitchToken
from backend.app.repositories.token_repository import TokenRepository

logger = logging.getLogger(__name__)

class TwitchError(HTTPException):
    def __init__(self, status_code: int, message: str):
        super().__init__(
            status_code=status_code,
            detail={
                "error": message,
                "docs_url": "https://dev.twitch.tv/docs"
            }
        )

class TwitchAuthService:
    def __init__(self, token_repository: TokenRepository):
        self.settings = get_twitch_settings()
        self.token_repository = token_repository
        self.client = httpx.AsyncClient()
        # Cache local pour stocker le token pendant 1 heure
        self._token_cache = TTLCache(maxsize=1, ttl=3600)

    async def get_valid_token(self) -> TwitchToken:
        """
        Récupère un token valide, en le renouvelant si nécessaire.
        Utilise un cache local TTL de 1 heure.
        """
        try:
            # Vérifier le cache local d'abord
            if "current_token" in self._token_cache:
                return self._token_cache["current_token"]

            current_token = await self.token_repository.get_current_token()
            
            if current_token and await self._is_token_valid(current_token):
                logger.debug("Token existant valide trouvé")
                self._token_cache["current_token"] = current_token
                return current_token
                
            logger.info("Génération d'un nouveau token")
            new_token = await self._generate_new_token()
            self._token_cache["current_token"] = new_token
            return new_token
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du token: {str(e)}")
            raise TwitchError(500, "Erreur d'authentification Twitch")

    async def _generate_new_token(self) -> TwitchToken:
        """
        Génère un nouveau token d'accès via l'API Twitch.
        """
        try:
            data = {
                "client_id": self.settings.client_id,
                "client_secret": "***",  # Masqué pour les logs
                "grant_type": "client_credentials"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            logger.info(f"[Twitch Auth Request] POST {self.settings.token_url}")
            logger.info(f"[Twitch Auth Request] Headers: {headers}")
            logger.info(f"[Twitch Auth Request] Data: {data}")
            
            async with self.client as client:
                response = await client.post(
                    self.settings.token_url,
                    data={
                        "client_id": self.settings.client_id,
                        "client_secret": self.settings.client_secret,
                        "grant_type": "client_credentials"
                    },
                    headers=headers
                )
                
                logger.info(f"[Twitch Auth Response] Status: {response.status_code}")
                if response.status_code != 200:
                    logger.error(f"[Twitch Auth Error] Response: {response.text}")
                
                if response.status_code == 429:
                    raise TwitchError(429, "Rate limit exceeded")
                    
                response.raise_for_status()
                data = response.json()
                logger.info("[Twitch Auth Response] Token generated successfully")
                
            expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
            
            token = TwitchToken(
                access_token=data["access_token"],
                expires_at=expires_at,
                token_type=data["token_type"]
            )
            
            await self.token_repository.save_token(token)
            logger.info(f"[Twitch Auth] Token saved, expires at: {expires_at}")
            return token
            
        except httpx.HTTPError as e:
            logger.error(f"[Twitch Auth Error] HTTP error generating token: {str(e)}")
            raise TwitchError(500, f"Impossible de générer un token Twitch: {str(e)}")
        except Exception as e:
            logger.error(f"[Twitch Auth Error] Internal error: {str(e)}")
            raise TwitchError(500, "Erreur interne du serveur")

    async def _is_token_valid(self, token: TwitchToken) -> bool:
        """
        Vérifie si le token est valide et non expiré.
        Renouvelle le token s'il expire bientôt.
        """
        if not token.is_valid:
            logger.info("[Twitch Auth] Token marked as invalid")
            return False
            
        now = datetime.utcnow()
        
        # Si le token expire dans moins d'une heure
        if token.expires_at - now < timedelta(seconds=self.settings.token_refresh_before_expiry):
            logger.info(f"[Twitch Auth] Token expires soon (at {token.expires_at})")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {token.access_token}",
                "Client-Id": self.settings.client_id
            }
            
            logger.info(f"[Twitch Auth Request] GET {self.settings.validate_url}")
            logger.info(f"[Twitch Auth Request] Headers: {headers}")
            
            async with self.client as client:
                response = await client.get(self.settings.validate_url, headers=headers)
                
                logger.info(f"[Twitch Auth Response] Status: {response.status_code}")
                if response.status_code != 200:
                    logger.info(f"[Twitch Auth Response] Body: {response.text}")
                
                if response.status_code == 429:
                    raise TwitchError(429, "Rate limit exceeded")
                    
                if response.status_code == 200:
                    await self.token_repository.update_last_used(token)
                    logger.info("[Twitch Auth] Token validated successfully")
                    return True
                
            logger.warning(f"[Twitch Auth] Invalid token response: {response.status_code}")
            await self.token_repository.invalidate_token(token)
            return False
            
        except httpx.HTTPError as e:
            logger.error(f"[Twitch Auth Error] HTTP error validating token: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[Twitch Auth Error] Internal error: {str(e)}")
            return False

    async def close(self):
        """
        Ferme proprement le client HTTP.
        """
        await self.client.aclose() 