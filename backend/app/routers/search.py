from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.twitch import TwitchSearchResult
from ..services.twitch_service import TwitchService

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/", response_model=TwitchSearchResult)
async def search_videos(
    game: str = Query(..., description="Nom du jeu à rechercher"),
    limit: int = Query(24, ge=1, le=100, description="Nombre de résultats par page"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    use_cache: bool = Query(True, description="Utiliser le cache")
):
    """
    Recherche des vidéos pour un jeu spécifique.
    - Supporte la pagination
    - Cache configurable
    - Limite de résultats paramétrable
    """
    try:
        # Initialiser le service Twitch
        twitch_service = TwitchService()
        
        try:
            # Calculer l'offset pour la pagination
            offset = (page - 1) * limit
            
            # Rechercher les vidéos
            result = await twitch_service.search_videos_by_game(
                game_name=game,
                limit=limit,
                offset=offset,
                use_cache=use_cache
            )
            return result
        finally:
            # S'assurer de fermer le client
            await twitch_service.close()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche des vidéos: {str(e)}"
        ) 