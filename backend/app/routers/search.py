from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from fastapi_cache.decorator import cache # Added for FastAPICache
from ..models.twitch import TwitchSearchResult
from ..services.twitch_service import TwitchService
from ..dependencies import get_twitch_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/", response_model=TwitchSearchResult)
@cache(expire=3600) # Cache for 1 hour
async def search_videos(
    game: str = Query(..., description="Nom du jeu à rechercher"),
    limit: int = Query(100, ge=1, le=100, description="Nombre de résultats à retourner (max 100)"),
    use_cache: bool = Query(True, description="Utiliser le cache"),
    after: Optional[str] = Query(None, description="Curseur pour la pagination"),
    twitch_service: TwitchService = Depends(get_twitch_service)
):
    """
    Recherche des vidéos pour un jeu spécifique.
    
    - Limite de 100 résultats par requête
    - Support de la pagination par curseur
    - Cache configurable
    - Tri par popularité (streams en direct en premier)
    """
    try:
        logger.info(f"Recherche de vidéos pour {game} (limit: {limit}, cache: {use_cache}, cursor: {after})")
        
        result = await twitch_service.search_videos_by_game(
            game_name=game,
            limit=limit,
            cursor=after,
            use_cache=use_cache
        )
        
        logger.info(f"Trouvé {result.total_count} vidéos pour {game}")
        return result
        
    except HTTPException as he:
        logger.error(f"Erreur HTTP pendant la recherche: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Erreur pendant la recherche: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche de vidéos: {str(e)}"
        )
    finally:
        await twitch_service.close() 