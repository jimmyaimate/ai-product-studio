from __future__ import annotations

import json

from agents.base_agent import BaseAgent
from core.task_queue.schemas import AgentOutput, TaskPayload


class StrategyAgent(BaseAgent):
    agent_name = "strategy"

    def run(self, task: TaskPayload) -> AgentOutput:
        system_prompt = self._load_versioned_prompt("strategy")
        brief = task.input_data.get("brief", "")
        template = task.input_data.get("template", "saas")

        lessons = self.learning_system.load_lessons(self.agent_name)
        lessons_text = "\n".join(f"- {l}" for l in lessons) if lessons else "None yet."

        memory_context = self._get_relevant_memory(brief, task.project_id)
        memory_text = "\n".join(memory_context) if memory_context else "No prior context."

        messages = [
            {
                "role": "user",
                "content": (
                    f"Product Brief:\n{brief}\n\n"
                    f"Template type: {template}\n\n"
                    f"Prior lessons:\n{lessons_text}\n\n"
                    f"Relevant project context:\n{memory_text}\n\n"
                    "Produce: business model, GTM strategy, feature prioritization (MoSCoW), "
                    "revenue model, and 3-month roadmap. Format as structured JSON."
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

        self._store_output(task.project_id, text, {"agent": self.agent_name, "task_id": task.task_id})
        self.learning_system.record_lesson(
            task.project_id, self.agent_name,
            "Completed strategy analysis for brief: " + brief[:100]
        )

        return AgentOutput(
            task_id=task.task_id,
            agent_type=self.agent_name,
            project_id=task.project_id,
            status="completed",
            output=output,
            tokens_used=prompt_tokens + completion_tokens,
        )
