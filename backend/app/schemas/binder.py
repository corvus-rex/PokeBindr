from datetime import datetime

from pydantic import BaseModel, Field


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
    position: int = Field(ge=0)
    card: CardSummary


class BinderDetailResponse(BinderResponse):
    cards: list[BinderCardEntry]

class BinderCardUpdate(BaseModel):
    card_id: str
    position: int = Field(ge=0)

class BinderPublicSummary(BaseModel):
    id: str
    title: str
    owner_id: str
    slug: str
    created_at: datetime
    cover_images: list[str]

class BinderUpdateRequest(BaseModel):
    cards: list[BinderCardUpdate]