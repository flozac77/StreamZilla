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

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Prometheus metrics
instrumentator = Instrumentator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.ENVIRONMENT == "dev":
        # En développement, utiliser le cache en mémoire
        FastAPICache.init(InMemoryBackend(), prefix="visibrain-cache")
        logger.info("Using in-memory cache for development")
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
    if settings.ENVIRONMENT != "dev":
        await redis_instance.close()

# Init FastAPI
app = FastAPI(
    title="Twitch Video Search API",
    description="API pour rechercher des vidéos de jeux sur Twitch",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Instrument FastAPI with Prometheus
instrumentator.instrument(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
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
app.include_router(twitch.router, prefix="/api/twitch", tags=["twitch"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World"} 