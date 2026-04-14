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

        # Log request: only method and path (no headers)
        logger.info(f"{request.method} {request.url.path}")

        # Execute request
        response = await call_next(request)

        # Calculate duration
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)

        # Log response: status and duration
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - "
            f"{formatted_process_time}ms"
        )

        return response
