import logging
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
import sys
# FastAPI imports
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

# Local imports
from .routers.search import router as search_router
from .routers.auth import router as auth_router
from .config import settings
from .cache_config import setup_cache
from .scheduler import CacheScheduler
from .config.logging_config import setup_logging
from .middleware.logging import RequestLoggingMiddleware

# Configuration des logs
setup_logging()  # Utilise notre nouvelle configuration
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
    
    logger.warning("Application démarrée avec succès")  # Changé en WARNING
    yield

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        await client[settings.MONGODB_DB_NAME].command("ping")
        logger.warning("✅ MongoDB Atlas ping OK from Vercel")  # Changé en WARNING
    except Exception as e:
        logger.error(f"❌ MongoDB Atlas ping failed from Vercel: {e}")
    yield
    
    # Shutdown
    if scheduler:
        await scheduler.stop()
        logger.warning("Application arrêtée avec succès")  # Changé en WARNING

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

# Ajout du middleware de logging en premier
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(search_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 