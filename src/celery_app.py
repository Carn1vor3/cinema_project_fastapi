from celery import Celery
from celery.schedules import crontab
from src.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "cinema_app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["src.tasks.activation_tokens"]
)

celery_app.conf.beat_schedule = {
    "delete-expired-activation-tokens": {
        "task": "src.tasks.activation_tokens.delete_expired_tokens",
        "schedule": 3600.0,
    },
}

celery_app.autodiscover_tasks(["src.tasks"])
