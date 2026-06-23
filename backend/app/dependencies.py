from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import database


def get_database() -> AsyncIOMotorDatabase:
    if database.db is None:
        raise RuntimeError("Database is not initialized")
    return database.db