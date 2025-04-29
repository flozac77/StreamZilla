import logging
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

# Local imports
from backend.app.routers.search import router as search_router
from backend.app.routers.auth import router as auth_router
from backend.app.config import settings
from backend.app.cache_config import setup_cache
from backend.app.scheduler import CacheScheduler

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable pour stocker le scheduler
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scheduler
    
    # Configuration du cache
    await setup_cache()
    
    # Initialisation du scheduler
    scheduler = CacheScheduler(cache_ttl=3600)  # 1 heure
    await scheduler.start()
    
    logger.info("Application démarrée avec succès")
    yield
    
    # Shutdown
    if scheduler:
        await scheduler.stop()
        logger.info("Application arrêtée avec succès")

# Définition des valeurs pour FastAPI
PROJECT_NAME = "VisioBrain API"
API_V1_STR = "/api/v1"

# Init FastAPI
app = FastAPI(
    title=PROJECT_NAME,
    description="API pour la gestion des vidéos Twitch",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url=f"{API_V1_STR}/openapi.json",
    lifespan=lifespan,
    debug=True
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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