import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

from app.dependencies import get_database, get_current_user
from app.schemas.binder import (
    BinderCardAddRequest,
    BinderCardEntry,
    BinderCreateRequest,
    BinderUpdateRequest,
    BinderDetailResponse,
    BinderPublicSummary,
    BinderResponse,
    CardSummary,
)

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


async def _get_binder_or_404(binder_id: str, db: AsyncIOMotorDatabase) -> dict:
    try:
        object_id = ObjectId(binder_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binder not found")

    binder = await db["binders"].find_one({"_id": object_id})
    if binder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binder not found")

    return binder


async def _get_owned_binder(
    binder_id: str, owner_id: str, db: AsyncIOMotorDatabase
) -> dict:
    binder = await _get_binder_or_404(binder_id, db)

    if binder["owner_id"] != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this binder",
        )

    return binder


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

@router.get("/users/{user_id}", response_model=list[BinderResponse])
async def list_user_binders(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    binders = await db["binders"].find(
        {"owner_id": user_id}
    ).to_list(length=None)

    return [_to_response(b) for b in binders]

@router.get("/public/recent", response_model=list[BinderPublicSummary])
async def list_recent_public_binders(
    limit: int = Query(default=8, ge=1, le=20),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    cursor = db["binders"].find().sort("created_at", -1).limit(limit)
    binders = await cursor.to_list(length=limit)

    results: list[BinderPublicSummary] = []
    for b in binders:
        binder_id = str(b["_id"])
        covers_cursor = (
            db["binder_cards"]
            .find({"binder_id": binder_id}, {"_id": 0, "images": 1})
            .sort("position", 1)
            .limit(3)
        )
        covers = await covers_cursor.to_list(length=3)
        cover_images = [c["images"]["small"] for c in covers if "images" in c]

        results.append(
            BinderPublicSummary(
                id=binder_id,
                title=b["title"],
                owner_id=b["owner_id"],
                slug=b["slug"],
                created_at=b["created_at"],
                cover_images=cover_images,
            )
        )

    return results

@router.get("/{binder_id}", response_model=BinderDetailResponse)
async def get_binder(
    binder_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    binder = await _get_binder_or_404(binder_id, db)

    entries_cursor = db["binder_cards"].find({"binder_id": binder_id}).sort("position", 1)
    entries = await entries_cursor.to_list(length=None)

    resolved_cards = [
        BinderCardEntry(
            position=e["position"],
            card=CardSummary(id=e["card_id"], name=e["name"], images=e["images"]),
        )
        for e in entries
    ]

    response = _to_response(binder).model_dump()
    response["cards"] = resolved_cards
    return BinderDetailResponse(**response)


@router.post(
    "/{binder_id}/cards",
    response_model=BinderCardEntry,
    status_code=status.HTTP_201_CREATED,
)
async def add_card_to_binder(
    binder_id: str,
    payload: BinderCardAddRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await _get_owned_binder(binder_id, str(current_user["_id"]), db)

    card = await db["cards"].find_one(
        {"id": payload.card_id}, {"_id": 0, "id": 1, "name": 1, "images": 1}
    )
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    last_entry = await db["binder_cards"].find_one(
        {"binder_id": binder_id}, sort=[("position", -1)]
    )
    next_position = (last_entry["position"] + 1) if last_entry else 0

    entry_doc = {
        "binder_id": binder_id,
        "card_id": card["id"],
        "name": card["name"],
        "images": card["images"],
        "position": next_position,
        "added_at": datetime.now(timezone.utc),
    }
    await db["binder_cards"].insert_one(entry_doc)

    return BinderCardEntry(
        position=next_position,
        card=CardSummary(id=card["id"], name=card["name"], images=card["images"]),
    )

@router.put("/{binder_id}", response_model=BinderDetailResponse)
async def update_binder(
    binder_id: str,
    payload: BinderUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await _get_owned_binder(
        binder_id,
        str(current_user["_id"]),
        db,
    )

    positions = [c.position for c in payload.cards]

    if len(positions) != len(set(positions)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate positions are not allowed",
        )

    card_ids = [c.card_id for c in payload.cards]

    cards = await db["cards"].find(
        {"id": {"$in": card_ids}},
        {"_id": 0, "id": 1, "name": 1, "images": 1},
    ).to_list(None)

    cards_by_id = {c["id"]: c for c in cards}

    missing = [cid for cid in card_ids if cid not in cards_by_id]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown card ids: {missing}",
        )

    await db["binder_cards"].delete_many({"binder_id": binder_id})

    if payload.cards:
        docs = []

        for entry in payload.cards:
            card = cards_by_id[entry.card_id]

            docs.append(
                {
                    "binder_id": binder_id,
                    "card_id": card["id"],
                    "name": card["name"],
                    "images": card["images"],
                    "position": entry.position,
                    "added_at": datetime.now(timezone.utc),
                }
            )

        await db["binder_cards"].insert_many(docs)

    binder = await _get_binder_or_404(binder_id, db)

    resolved_cards = [
        BinderCardEntry(
            position=e.position,
            card=CardSummary(
                id=cards_by_id[e.card_id]["id"],
                name=cards_by_id[e.card_id]["name"],
                images=cards_by_id[e.card_id]["images"],
            ),
        )
        for e in payload.cards
    ]

    response = _to_response(binder).model_dump()
    response["cards"] = resolved_cards

    return BinderDetailResponse(**response)

@router.delete("/{binder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_binder(
    binder_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    binder = await _get_owned_binder(binder_id, str(current_user["_id"]), db)
    await db["binders"].delete_one({"_id": binder["_id"]})
    await db["binder_cards"].delete_many({"binder_id": binder_id})