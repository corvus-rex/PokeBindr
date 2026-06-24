from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, database
from app.routers import auth, cards, binders
from app.seed import seed_cards


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"},
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await seed_cards(database.db)
    yield
    await close_mongo_connection()


app = FastAPI(title="PokeBindr API", lifespan=lifespan)

app.add_middleware(MaxBodySizeMiddleware, max_size=settings.max_request_body_size)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(binders.router)


@app.get("/health")
def health_check():
    return {"status": "Gotta catch 'em all!"}