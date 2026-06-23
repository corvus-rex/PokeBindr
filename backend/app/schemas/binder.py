from datetime import datetime

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


class CardSummary(BaseModel):
    id: str
    name: str
    images: dict[str, str]


class BinderCardEntry(BaseModel):
    position: int
    card: CardSummary


class BinderDetailResponse(BinderResponse):
    cards: list[BinderCardEntry]