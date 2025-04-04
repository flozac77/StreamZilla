import logging
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# Local imports
from backend.app.routers.search import router as search_router
from backend.app.routers.auth import router as auth_router
from backend.app.config import settings

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    FastAPICache.init(InMemoryBackend(), prefix="dbTwitch-cache")
    logger.info("Using in-memory cache for development")
    yield

# Init FastAPI
app = FastAPI(
    title="VisioBrain API",
    description="API pour la gestion des vidéos Twitch",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    debug=True
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie="twitch_session",
    max_age=3600,  # 1 hour
)

# Include routers
app.include_router(search_router)
app.include_router(auth_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.get("/")
async def root():
    return {"message": "VisioBrain API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 