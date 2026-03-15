from __future__ import annotations

import json
import time
import uuid
import logging
from typing import Any

from config.settings import Settings
from core.credits.tracker import CreditTracker
from core.task_queue.celery_app import celery_app
from core.task_queue.schemas import AgentOutput, TaskPayload
from memory.learning_system.learning import LearningSystem
from memory.project_memory.project_store import ProjectStore
from memory.vector_memory.base import VectorStoreBase

logger = logging.getLogger(__name__)


class OpenClawJimmy:
    """Manager agent that orchestrates the full AI Product Studio pipeline."""

    AGENT_SEQUENCE = [
        "research",
        "strategy",
        "ux",
        "ui",
        "automation",
        "documentation",
    ]

    def __init__(
        self,
        settings: Settings,
        credit_tracker: CreditTracker,
        vector_store: VectorStoreBase,
        learning_system: LearningSystem,
    ):
        self.settings = settings
        self.credit_tracker = credit_tracker
        self.vector_store = vector_store
        self.learning_system = learning_system
        self.project_store = ProjectStore(settings)

    def handle_project(self, project_brief: str, project_id: str | None = None, template: str = "saas") -> dict[str, Any]:
        """Full orchestration: dispatch all agents, wait, compile."""
        project_id = project_id or str(uuid.uuid4())
        logger.info("Jimmy starting project %s | template=%s", project_id, template)

        # Save brief
        self.project_store.save_context(project_id, "brief", {"brief": project_brief, "template": template})

        dispatched: list[tuple[str, str]] = []  # (agent_type, celery_task_id)

        # Sequential pipeline (each agent may use previous outputs)
        accumulated_outputs: dict[str, Any] = {}

        for agent_type in self.AGENT_SEQUENCE:
            input_data = self._build_input_data(agent_type, project_brief, template, accumulated_outputs)
            celery_id = self.dispatch_task(agent_type, input_data, project_id=project_id)
            dispatched.append((agent_type, celery_id))
            logger.info("Dispatched %s → celery task %s", agent_type, celery_id)

            # Wait for this task before proceeding (sequential pipeline)
            result = self._wait_for_task(celery_id, timeout=300)
            if result:
                accumulated_outputs[agent_type] = result.get("output", {})
                self.project_store.save_agent_output(project_id, agent_type, result.get("output", {}))

        final = self.compile_outputs(project_id)
        logger.info("Jimmy completed project %s", project_id)
        return {"project_id": project_id, "status": "completed", "outputs": final, "credits": self.credit_tracker.summary()}

    def dispatch_task(self, agent_type: str, input_data: dict[str, Any], project_id: str, priority: int = 5) -> str:
        payload = TaskPayload(
            agent_type=agent_type,
            priority=priority,
            project_id=project_id,
            input_data=input_data,
        )
        result = celery_app.send_task(
            "core.task_queue.tasks.run_agent_task",
            args=[payload.model_dump()],
            queue="agents",
            priority=priority,
        )
        return result.id

    def _wait_for_task(self, celery_task_id: str, timeout: int = 300, poll_interval: float = 2.0) -> dict | None:
        from celery.result import AsyncResult
        result = AsyncResult(celery_task_id, app=celery_app)
        elapsed = 0.0
        while elapsed < timeout:
            if result.ready():
                if result.successful():
                    return result.get()
                else:
                    logger.error("Task %s failed: %s", celery_task_id, result.info)
                    return None
            time.sleep(poll_interval)
            elapsed += poll_interval
        logger.warning("Task %s timed out after %ds", celery_task_id, timeout)
        return None

    def wait_for_tasks(self, task_ids: list[str], timeout: int = 600) -> dict[str, dict | None]:
        return {tid: self._wait_for_task(tid, timeout=timeout) for tid in task_ids}

    def compile_outputs(self, project_id: str) -> dict[str, Any]:
        return self.project_store.compile_all_outputs(project_id)

    def get_project_status(self, project_id: str) -> dict[str, Any]:
        outputs = self.project_store.list_outputs(project_id)
        completed_agents = [o.replace("output_", "").replace("_latest", "") for o in outputs if o.endswith("_latest")]
        return {
            "project_id": project_id,
            "completed_agents": completed_agents,
            "pending_agents": [a for a in self.AGENT_SEQUENCE if a not in completed_agents],
            "credits": self.credit_tracker.summary(),
        }

    def _build_input_data(
        self, agent_type: str, brief: str, template: str, accumulated: dict[str, Any]
    ) -> dict[str, Any]:
        base = {"brief": brief, "template": template}
        if agent_type == "ux":
            base["personas"] = accumulated.get("research", {}).get("personas", [])
        elif agent_type == "ui":
            base["ux_output"] = accumulated.get("ux", {})
        elif agent_type == "automation":
            base["strategy_output"] = accumulated.get("strategy", {})
        elif agent_type == "documentation":
            base["all_outputs"] = accumulated
        return base
