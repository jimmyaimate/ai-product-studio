from __future__ import annotations

import json

from agents.base_agent import BaseAgent
from core.task_queue.schemas import AgentOutput, TaskPayload


class DocumentationAgent(BaseAgent):
    agent_name = "documentation"

    def run(self, task: TaskPayload) -> AgentOutput:
        system_prompt = self._load_versioned_prompt("documentation")
        brief = task.input_data.get("brief", "")
        all_outputs = task.input_data.get("all_outputs", {})

        messages = [
            {
                "role": "user",
                "content": (
                    f"Product Brief:\n{brief}\n\n"
                    f"All Agent Outputs:\n{json.dumps(all_outputs, indent=2)}\n\n"
                    "Produce: full PRD (executive summary, features, tech stack, timelines), "
                    "README.md content, API documentation outline, onboarding guide, "
                    "and key architectural decisions. Format as structured JSON with "
                    "markdown strings for document content."
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
