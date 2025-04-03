from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.twitch import TwitchSearchResult
from ..services.twitch_service import TwitchService

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/", response_model=TwitchSearchResult)
async def search_videos(
    game: str = Query(..., description="Game name to search for"),
    limit: int = Query(24, ge=1, le=100, description="Number of results per page"),
    page: int = Query(1, ge=1, description="Page number"),
    use_cache: bool = Query(True, description="Use cache")
):
    """
    Search videos for a specific game.
    - Supports pagination
    - Configurable cache
    - Configurable result limit
    """
    try:
        # Initialize Twitch service
        twitch_service = TwitchService()
        
        try:
            # Calculate pagination offset
            offset = (page - 1) * limit
            
            # Search videos
            result = await twitch_service.search_videos_by_game(
                game_name=game,
                limit=limit,
                offset=offset,
                use_cache=use_cache
            )
            return result
        finally:
            # Ensure client is closed
            await twitch_service.close()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while searching videos: {str(e)}"
        ) 