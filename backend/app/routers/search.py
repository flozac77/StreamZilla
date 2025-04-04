from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.twitch import TwitchSearchResult
from ..services.twitch_service import TwitchService

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/", response_model=TwitchSearchResult)
async def search_videos(
    game: str = Query(..., description="Game name to search for"),
    limit: int = Query(100, ge=1, le=100, description="Number of results to return (max 100)"),
    use_cache: bool = Query(True, description="Use cache"),
    after: Optional[str] = Query(None, description="Cursor for pagination")
):
    """
    Search videos for a specific game.
    - Maximum 100 results per request
    - Supports cursor-based pagination
    - Configurable cache
    """
    try:
        # Initialize Twitch service
        twitch_service = TwitchService()
        
        try:
            # Search videos
            result = await twitch_service.search_videos_by_game(
                game_name=game,
                limit=limit,
                cursor=after,
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