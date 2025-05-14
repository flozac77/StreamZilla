import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log la requête entrante
        logger.warning(f"[Request] {request.method} {request.url.path}")
        logger.warning(f"[Request Headers] {dict(request.headers)}")
        
        # Exécute la requête
        response = await call_next(request)
        
        # Calcule la durée
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        
        # Log la réponse
        logger.warning(
            f"[Response] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {formatted_process_time}ms"
        )
        
        return response 