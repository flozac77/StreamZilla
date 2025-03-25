import logging
from datetime import datetime, timedelta
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import DESCENDING

from backend.app.models.token import TwitchToken

logger = logging.getLogger(__name__)

class TokenRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.twitch_tokens

    async def initialize(self):
        """
        Initialise les index nécessaires.
        """
        await self.collection.create_index([("created_at", DESCENDING)])
        await self.collection.create_index("is_valid")

    async def save_token(self, token: TwitchToken) -> None:
        """
        Sauvegarde un nouveau token dans la base de données.
        """
        try:
            token_dict = token.model_dump()
            token_dict["created_at"] = datetime.utcnow()
            
            await self.collection.insert_one(token_dict)
            logger.info("Token sauvegardé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du token: {str(e)}")
            raise

    async def get_current_token(self) -> Optional[TwitchToken]:
        """
        Récupère le token le plus récent et valide de la base de données.
        """
        try:
            # Chercher le token le plus récent qui n'est pas expiré
            token_doc = await self.collection.find_one(
                {"expires_at": {"$gt": datetime.utcnow()}},
                sort=[("created_at", -1)]
            )
            
            if token_doc:
                return TwitchToken(**token_doc)
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du token: {str(e)}")
            return None

    async def update_last_used(self, token: TwitchToken) -> None:
        """
        Met à jour la date de dernière utilisation d'un token.
        """
        try:
            await self.collection.update_one(
                {"access_token": token.access_token},
                {"$set": {"last_used": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du token: {str(e)}")

    async def invalidate_token(self, token: TwitchToken) -> None:
        """
        Marque un token comme invalide dans la base de données.
        """
        try:
            await self.collection.update_one(
                {"access_token": token.access_token},
                {"$set": {"is_valid": False}}
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'invalidation du token: {str(e)}")
            raise

    async def cleanup_old_tokens(self, days: int = 7) -> None:
        """
        Supprime les vieux tokens invalides.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await self.collection.delete_many({
                "is_valid": False,
                "created_at": {"$lt": cutoff_date}
            })
            logger.info(f"Nettoyage des vieux tokens: {result.deleted_count} supprimés")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des vieux tokens: {str(e)}")
            raise 