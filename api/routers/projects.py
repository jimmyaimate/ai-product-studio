from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.manager_agent.jimmy import OpenClawJimmy
from api.deps import CreditsDep, LearnDep, SettingsDep, VectorStoreDep

router = APIRouter()


class CreateProjectRequest(BaseModel):
    brief: str
    template: str = "saas"
    name: str = ""


class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str


@router.post("", response_model=ProjectResponse)
async def create_project(
    req: CreateProjectRequest,
    settings: SettingsDep,
    credits: CreditsDep,
    vector_store: VectorStoreDep,
    learn: LearnDep,
):
    project_id = str(uuid.uuid4())
    jimmy = OpenClawJimmy(
        settings=settings,
        credit_tracker=credits,
        vector_store=vector_store,
        learning_system=learn,
    )
    # Dispatch async via Celery (non-blocking)
    jimmy.dispatch_task(
        "research",
        {"brief": req.brief, "template": req.template},
        project_id=project_id,
    )
    return ProjectResponse(
        project_id=project_id,
        status="started",
        message=f"Project {project_id} dispatched. Poll /projects/{project_id}/status for updates.",
    )


@router.get("/{project_id}")
async def get_project(project_id: str, settings: SettingsDep) -> dict[str, Any]:
    from memory.project_memory.project_store import ProjectStore
    store = ProjectStore(settings)
    brief = store.load_context(project_id, "brief")
    if brief is None:
        raise HTTPException(status_code=404, detail="Project not found")
    outputs = store.compile_all_outputs(project_id)
    return {"project_id": project_id, "brief": brief, "outputs": outputs}


@router.get("/{project_id}/status")
async def get_project_status(
    project_id: str,
    settings: SettingsDep,
    credits: CreditsDep,
    vector_store: VectorStoreDep,
    learn: LearnDep,
) -> dict[str, Any]:
    jimmy = OpenClawJimmy(
        settings=settings,
        credit_tracker=credits,
        vector_store=vector_store,
        learning_system=learn,
    )
    return jimmy.get_project_status(project_id)
