from __future__ import annotations

import json
import logging
from typing import Any

from celery import Task as CeleryTask

from core.task_queue.celery_app import celery_app
from core.task_queue.schemas import TaskPayload

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@celery_app.task(
    bind=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=5,
    name="core.task_queue.tasks.run_agent_task",
)
def run_agent_task(self: CeleryTask, payload_dict: dict[str, Any]) -> dict[str, Any]:
    """Generic Celery task that routes to the correct agent based on agent_type."""
    payload = TaskPayload(**payload_dict)

    try:
        from config.settings import get_settings
        from core.credits.tracker import CreditTracker
        from memory.vector_memory.factory import get_vector_store
        from memory.learning_system.learning import LearningSystem
        from agents.base_agent import get_agent_for_type

        settings = get_settings()
        credit_tracker = CreditTracker(settings)
        vector_store = get_vector_store(settings)
        learning_system = LearningSystem(settings)

        agent = get_agent_for_type(
            payload.agent_type,
            settings=settings,
            credit_tracker=credit_tracker,
            vector_store=vector_store,
            learning_system=learning_system,
        )
        result = agent.run(payload)
        return result.model_dump()

    except Exception as exc:
        logger.exception("Task %s failed (attempt %d): %s", payload.task_id, self.request.retries, exc)
        if self.request.retries < MAX_RETRIES:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        return {
            "task_id": payload.task_id,
            "agent_type": payload.agent_type,
            "project_id": payload.project_id,
            "status": "failed",
            "output": {},
            "tokens_used": 0,
            "error": str(exc),
        }
