from typing import Any

from pydantic import BaseModel


class CardSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[dict[str, Any]]