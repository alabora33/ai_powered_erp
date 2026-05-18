"""
Celery application configuration and task definitions.
"""

from celery import Celery

from backend.config import settings

# ─── Celery App ───────────────────────────────────────────────────────────────

celery_app = Celery(
    "ai_erp",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["backend.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Istanbul",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,  # 24 hours
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
    broker_connection_retry_on_startup=True,
)
