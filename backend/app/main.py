from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.routes import twitch
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis cache
    redis = RedisBackend(settings.REDIS_URL)
    FastAPICache.init(redis, prefix="visibrain-cache")
    yield
    # Cleanup code (if needed)

# Init FastAPI
app = FastAPI(
    title="Visibrain API",
    description="API pour l'application Visibrain",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY
)

# Include routers
app.include_router(twitch.router, prefix="/api/twitch", tags=["twitch"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World"} 