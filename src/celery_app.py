from celery import Celery

celery_app = Celery("cinema_app")
celery_app.config_from_object("src.settings", namespace="CELERY")
celery_app.autodiscover_tasks(["src.tasks"])

celery_app.conf.beat_schedule = {
    "delete-expired-activation-tokens": {
        "task": "src.tasks.activation_tokens.delete_expired_tokens",
        "schedule": 3600.0,
    },
}