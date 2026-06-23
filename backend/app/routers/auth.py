from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_database
from app.schemas.user import UserRegisterRequest, UserResponse
from app.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    existing_user = await db["users"].find_one({"email": payload.email})
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user_doc = {
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }

    result = await db["users"].insert_one(user_doc)

    return UserResponse(
        id=str(result.inserted_id),
        email=user_doc["email"],
        created_at=user_doc["created_at"],
    )