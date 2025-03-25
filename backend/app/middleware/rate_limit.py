from fastapi import Request, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware pour gérer le rate limiting global
    """
    try:
        # Vérifier le rate limit pour l'IP
        await FastAPILimiter.check_rate_limit(request)
        response = await call_next(request)
        return response
    except HTTPException as e:
        if e.status_code == 429:  # Too Many Requests
            return {"error": "Rate limit exceeded", "message": str(e.detail)}
        raise e 