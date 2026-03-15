from __future__ import annotations

import json

from agents.base_agent import BaseAgent
from core.task_queue.schemas import AgentOutput, TaskPayload


class UXAgent(BaseAgent):
    agent_name = "ux"

    def run(self, task: TaskPayload) -> AgentOutput:
        system_prompt = self._load_versioned_prompt("ux")
        brief = task.input_data.get("brief", "")
        personas = task.input_data.get("personas", [])

        messages = [
            {
                "role": "user",
                "content": (
                    f"Product Brief:\n{brief}\n\n"
                    f"User Personas:\n{json.dumps(personas, indent=2)}\n\n"
                    "Produce: user journey maps (happy path + edge cases), information architecture, "
                    "key user flows (onboarding, core action, settings), wireframe prompts for UXPilot, "
                    "and accessibility checklist. Format as structured JSON."
                ),
            }
        ]

        text, prompt_tokens, completion_tokens = self._call_claude(
            messages, system_prompt, self.settings.max_tokens_per_task
        )

        try:
            output = json.loads(text)
        except json.JSONDecodeError:
            output = {"raw": text}

        self._store_output(task.project_id, text, {"agent": self.agent_name})

        return AgentOutput(
            task_id=task.task_id,
            agent_type=self.agent_name,
            project_id=task.project_id,
            status="completed",
            output=output,
            tokens_used=prompt_tokens + completion_tokens,
        )
