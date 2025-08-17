from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import engine
from models.movies import Base
from routers import movies

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(movies.router)
