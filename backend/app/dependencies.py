from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

from app.config import settings
from app.database import database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_database() -> AsyncIOMotorDatabase:
    if database.db is None:
        raise RuntimeError("Database is not initialized")
    return database.db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        raise credentials_error

    user = await db["users"].find_one({"_id": object_id})
    if user is None:
        raise credentials_error

    return user