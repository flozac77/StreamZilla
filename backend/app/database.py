# app/database.py
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.config import settings

def get_db():
    """Get a synchronous MongoDB connection"""
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    return db

async def get_async_db():
    """Get an asynchronous MongoDB connection"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    return db