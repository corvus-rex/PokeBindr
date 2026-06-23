from datetime import datetime

from pydantic import BaseModel, Field


class Binder(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    owner_id: str
    title: str
    description: str | None = None
    slug: str
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }