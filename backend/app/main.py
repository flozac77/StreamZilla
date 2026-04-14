import logging
from contextlib import asynccontextmanager
# FastAPI imports
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
    # === Startup ===
    global scheduler

    # Configuration du cache
    await setup_cache()

    # Initialisation du scheduler
    scheduler = CacheScheduler(cache_ttl=3600)
    await scheduler.start()

    logger.info("Application started")
    yield
    # === Shutdown ===
    if scheduler:
        await scheduler.stop()
    logger.info("Application stopped")

# Définition des valeurs pour FastAPI
PROJECT_NAME = "VisioBrain API"
API_V1_STR = "/api/v1"

# Init FastAPI
app = FastAPI(
    title=PROJECT_NAME,
    description="API pour la gestion des vidéos Twitch",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url=f"{API_V1_STR}/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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


@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 