from __future__ import annotations

from celery import Celery

from config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_product_studio",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["core.task_queue.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "core.task_queue.tasks.run_agent_task": {"queue": "agents"},
    },
)
