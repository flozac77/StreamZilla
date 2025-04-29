# FastAPI imports
from fastapi import APIRouter, Depends, HTTPException, Request

# Local imports
from ..services.twitch_service import TwitchService
from ..models.twitch import TwitchToken, TwitchUser

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/twitch/url")
async def get_auth_url():
    """Get Twitch OAuth URL"""
    twitch_service = TwitchService()
    try:
        url = await twitch_service.get_auth_url()
        return {"url": url}
    finally:
        await twitch_service.close()

@router.get("/twitch/callback")
async def auth_callback(code: str, request: Request):
    """Handle Twitch OAuth callback"""
    twitch_service = TwitchService()
    try:
        # Exchange code for token
        token = await twitch_service.exchange_code_for_token(code)
        
        # Get user info
        user = await twitch_service.get_user_info(token.access_token)
        
        # Store token in session
        request.session["twitch_token"] = token.dict()
        request.session["twitch_user"] = user.dict()
        
        return {"message": "Authentication successful"}
    finally:
        await twitch_service.close()

@router.get("/twitch/test")
async def test_auth(request: Request):
    """Test authentication status"""
    if "twitch_token" not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"message": "Authenticated", "user": request.session.get("twitch_user")} 