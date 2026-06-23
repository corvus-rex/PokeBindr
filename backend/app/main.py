from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import connect_to_mongo, close_mongo_connection, database
from app.routers import auth, cards
from app.seed import seed_cards


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await seed_cards(database.db)
    yield
    await close_mongo_connection()


app = FastAPI(title="PokeBindr API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(cards.router)

@app.get("/health")
def health_check():
    return {"status": "Gotta Catch 'em all!"}