import json
import logging
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings

logger = logging.getLogger(__name__)


async def seed_cards(db: AsyncIOMotorDatabase) -> None:
    collection = db["cards"]

    existing_count = await collection.count_documents({})
    if existing_count == 0:
        dataset_path = Path(settings.cards_dataset_path)
        with dataset_path.open("r", encoding="utf-8") as f:
            cards = json.load(f)

        if cards:
            await collection.insert_many(cards)
            logger.info("Seeded %d cards into the cards collection", len(cards))
    else:
        logger.info("Cards collection already has %d documents, skipping seed", existing_count)

    await collection.create_index("name")