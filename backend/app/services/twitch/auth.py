import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx
from fastapi import HTTPException
from fastapi_cache.decorator import cache

from backend.app.config.twitch import get_twitch_settings
from backend.app.models.token import TwitchToken
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

    @cache(expire=3600)  # Cache pour 1 heure
    async def get_valid_token(self) -> TwitchToken:
        """
        Récupère un token valide, en le renouvelant si nécessaire.
        Le résultat est mis en cache pendant 1 heure.
        """
        try:
            current_token = await self.token_repository.get_current_token()
            
            if current_token and await self._is_token_valid(current_token):
                logger.debug("Token existant valide trouvé")
                return current_token
                
            logger.info("Génération d'un nouveau token")
            return await self._generate_new_token()
            
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
                "client_secret": self.settings.client_secret,
                "grant_type": "client_credentials"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with self.client as client:
                response = await client.post(
                    self.settings.token_url,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 429:
                    raise TwitchError(429, "Rate limit exceeded")
                    
                response.raise_for_status()
                data = response.json()
                
            expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
            
            token = TwitchToken(
                access_token=data["access_token"],
                expires_at=expires_at,
                token_type=data["token_type"]
            )
            
            await self.token_repository.save_token(token)
            logger.info("Nouveau token généré et sauvegardé")
            return token
            
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP lors de la génération du token: {str(e)}")
            raise TwitchError(500, f"Impossible de générer un token Twitch: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur lors de la génération du token: {str(e)}")
            raise TwitchError(500, "Erreur interne du serveur")

    async def _is_token_valid(self, token: TwitchToken) -> bool:
        """
        Vérifie si le token est valide et non expiré.
        Renouvelle le token s'il expire bientôt.
        """
        if not token.is_valid:
            return False
            
        now = datetime.utcnow()
        
        # Si le token expire dans moins d'une heure
        if token.expires_at - now < timedelta(seconds=self.settings.token_refresh_before_expiry):
            logger.info("Token proche de l'expiration, renouvellement...")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {token.access_token}",
                "Client-Id": self.settings.client_id
            }
            
            async with self.client as client:
                response = await client.get(self.settings.validate_url, headers=headers)
                
                if response.status_code == 429:
                    raise TwitchError(429, "Rate limit exceeded")
                    
                if response.status_code == 200:
                    await self.token_repository.update_last_used(token)
                    return True
                
            logger.warning(f"Token invalide: {response.status_code}")
            await self.token_repository.invalidate_token(token)
            return False
            
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP lors de la validation du token: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la validation du token: {str(e)}")
            return False

    async def close(self):
        """
        Ferme proprement le client HTTP.
        """
        await self.client.aclose() 