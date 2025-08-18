from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


DATABASE_URL = "sqlite+aiosqlite:///./cinema_project.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
