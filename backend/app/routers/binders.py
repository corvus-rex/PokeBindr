import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

from app.dependencies import get_database, get_current_user
from app.schemas.binder import BinderCreateRequest, BinderResponse

router = APIRouter(prefix="/binders", tags=["binders"])


def _slugify(title: str) -> str:
    base = "-".join(title.strip().lower().split())
    base = "".join(c for c in base if c.isalnum() or c == "-")
    suffix = secrets.token_hex(3)
    return f"{base}-{suffix}" if base else suffix


def _to_response(doc: dict) -> BinderResponse:
    return BinderResponse(
        id=str(doc["_id"]),
        owner_id=doc["owner_id"],
        title=doc["title"],
        description=doc.get("description"),
        slug=doc["slug"],
        created_at=doc["created_at"],
    )


@router.post("", response_model=BinderResponse, status_code=status.HTTP_201_CREATED)
async def create_binder(
    payload: BinderCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    binder_doc = {
        "owner_id": str(current_user["_id"]),
        "title": payload.title,
        "description": payload.description,
        "slug": _slugify(payload.title),
        "created_at": datetime.now(timezone.utc),
    }

    result = await db["binders"].insert_one(binder_doc)
    binder_doc["_id"] = result.inserted_id

    return _to_response(binder_doc)


@router.get("", response_model=list[BinderResponse])
async def list_binders(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    owner_id = str(current_user["_id"])
    cursor = db["binders"].find({"owner_id": owner_id})
    binders = await cursor.to_list(length=None)
    return [_to_response(b) for b in binders]


@router.get("/{binder_id}", response_model=BinderResponse)
async def get_binder(
    binder_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        object_id = ObjectId(binder_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binder not found")

    binder = await db["binders"].find_one({"_id": object_id})

    if binder is None or binder["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binder not found")

    return _to_response(binder)


@router.delete("/{binder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_binder(
    binder_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        object_id = ObjectId(binder_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binder not found")

    binder = await db["binders"].find_one({"_id": object_id})

    if binder is None or binder["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binder not found")

    await db["binders"].delete_one({"_id": object_id})