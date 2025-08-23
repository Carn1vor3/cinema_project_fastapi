from datetime import datetime, timezone
from celery import shared_task
from sqlalchemy import delete
from src.database import AsyncSessionLocal
from src.models.users import ActivationToken
import asyncio

@shared_task
def delete_expired_tokens():
    return asyncio.run(_delete_expired_tokens())

async def _delete_expired_tokens():
    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc)
        stmt = delete(ActivationToken).where(ActivationToken.expires_at < now)
        result = await session.execute(stmt)
        await session.commit()
        return f"Deleted {result.rowcount or 0} expired activation tokens"
