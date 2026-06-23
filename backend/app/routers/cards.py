from typing import Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_database
from app.schemas.card import CardSearchResponse

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("/search", response_model=CardSearchResponse)
async def search_cards(
    name: Optional[str] = Query(default=None),
    rarity: Optional[str] = Query(default=None),
    supertype: Optional[str] = Query(default=None),
    types: Optional[str] = Query(default=None),
    id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    query: dict = {}

    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if rarity:
        query["rarity"] = rarity
    if supertype:
        query["supertype"] = supertype
    if types:
        query["types"] = types
    if id:
        query["id"] = id

    collection = db["cards"]

    total = await collection.count_documents(query)

    skip = (page - 1) * page_size
    cursor = collection.find(query, {"_id": 0}).skip(skip).limit(page_size)
    results = await cursor.to_list(length=page_size)

    return CardSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results,
    )