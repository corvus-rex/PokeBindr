from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    email: EmailStr
    password_hash: str
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }