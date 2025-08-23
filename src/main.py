from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.database import engine
from src.models.movies import Base
from src.routers import movies, users, auth, carts, orders, payments, stripe_webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(movies.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(carts.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(stripe_webhook.router)