from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(title="PokeBindr API", lifespan=lifespan)

app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "Gotta Catch 'em all!"}