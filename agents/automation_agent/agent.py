from __future__ import annotations

import json

from agents.base_agent import BaseAgent
from core.task_queue.schemas import AgentOutput, TaskPayload


class AutomationAgent(BaseAgent):
    agent_name = "automation"

    def run(self, task: TaskPayload) -> AgentOutput:
        system_prompt = self._load_versioned_prompt("automation")
        brief = task.input_data.get("brief", "")
        strategy_output = task.input_data.get("strategy_output", {})

        messages = [
            {
                "role": "user",
                "content": (
                    f"Product Brief:\n{brief}\n\n"
                    f"Strategy:\n{json.dumps(strategy_output, indent=2)}\n\n"
                    "Produce: integration specifications (auth, payments, notifications, analytics), "
                    "API endpoint list with request/response schemas, Claude Code task prompts "
                    "for each major feature, CI/CD pipeline recommendation, and deployment checklist. "
                    "Format as structured JSON."
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
