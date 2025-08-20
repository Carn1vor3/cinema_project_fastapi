from celery import Celery
from datetime import datetime, timezone
from sqlalchemy import delete
import asyncio

from database import AsyncSessionLocal
from models.users import ActivationToken, PasswordResetToken, RefreshToken

celery = Celery("tasks", broker="redis://localhost:6379/0")


def cleanup_tokens_sync():
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            for model in [ActivationToken, PasswordResetToken, RefreshToken]:
                await db.execute(delete(model).where(model.expires_at < now))
            await db.commit()

    asyncio.run(_cleanup())


@celery.task
def cleanup_tokens():
    cleanup_tokens_sync()
