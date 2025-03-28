from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from backend.app.routes import twitch
from backend.app.config import settings
from starlette.middleware.sessions import SessionMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from backend.app.middleware.rate_limit import rate_limit_middleware
import logging
from contextlib import asynccontextmanager

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Prometheus metrics
instrumentator = Instrumentator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis_instance = None
    if settings.ENVIRONMENT == "dev":
        # En développement, utiliser le cache en mémoire
        FastAPICache.init(InMemoryBackend(), prefix="visibrain-cache")
        # Désactiver le rate limiter en dev
        logger.info("Using in-memory cache for development, rate limiter disabled")
    else:
        # En production, utiliser Redis
        redis_instance = Redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis_instance), prefix="visibrain-cache")
        await FastAPILimiter.init(redis_instance)
        logger.info("Using Redis cache for production")

    # Expose Prometheus metrics
    instrumentator.expose(app)
    yield
    # Shutdown
    if redis_instance:
        await redis_instance.close()

# Init FastAPI
app = FastAPI(
    title="VisiBrain API",
    description="API pour la gestion des vidéos Twitch",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    debug=True  # Active le mode debug
)

# Instrument FastAPI with Prometheus
instrumentator.instrument(app)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend Vue.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit middleware (uniquement en production)
if settings.ENVIRONMENT != "dev":
    app.middleware("http")(rate_limit_middleware)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie="twitch_session",
    max_age=3600,  # 1 hour
)

# Include routers
app.include_router(twitch.router, prefix="/api", tags=["twitch"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")
    # Autres initialisations...

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
    # Nettoyage...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # reload=True pour le hot reload 