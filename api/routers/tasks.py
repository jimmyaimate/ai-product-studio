from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

router = APIRouter()


@router.get("/{task_id}")
async def get_task(task_id: str) -> dict[str, Any]:
    from core.task_queue.celery_app import celery_app
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
        "result": result.result if result.ready() and result.successful() else None,
        "error": str(result.info) if result.failed() else None,
    }


class RetryRequest(BaseModel):
    agent_type: str
    project_id: str
    input_data: dict[str, Any] = {}


@router.post("/{task_id}/retry")
async def retry_task(task_id: str, req: RetryRequest) -> dict[str, Any]:
    from core.task_queue.celery_app import celery_app
    from core.task_queue.schemas import TaskPayload
    payload = TaskPayload(
        task_id=task_id,
        agent_type=req.agent_type,
        project_id=req.project_id,
        input_data=req.input_data,
    )
    result = celery_app.send_task(
        "core.task_queue.tasks.run_agent_task",
        args=[payload.model_dump()],
        queue="agents",
    )
    return {"task_id": task_id, "new_celery_id": result.id, "status": "queued"}
