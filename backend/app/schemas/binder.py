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