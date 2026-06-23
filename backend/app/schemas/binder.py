from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BinderCreateRequest(BaseModel):
    title: str
    description: str | None = None


class BinderResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    description: str | None
    slug: str
    created_at: datetime


class BinderCardAddRequest(BaseModel):
    card_id: str


class BinderCardEntry(BaseModel):
    position: int
    card: dict[str, Any]


class BinderDetailResponse(BinderResponse):
    cards: list[BinderCardEntry]