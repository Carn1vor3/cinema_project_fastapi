
from datetime import datetime, UTC
from celery import shared_task
from sqlalchemy import delete

from database import AsyncSessionLocal
from models.users import ActivationToken


@shared_task
def delete_expired_tokens():
    import asyncio
    return asyncio.run(_delete_expired_tokens())


async def _delete_expired_tokens():
    async with AsyncSessionLocal as session:
        now = datetime.now(UTC)

        stmt = delete(ActivationToken).where(ActivationToken.expires_at < now)
        result = await session.execute(stmt)
        await session.commit()

        return f"Deleted {result.rowcount or 0} expired activation tokens"
