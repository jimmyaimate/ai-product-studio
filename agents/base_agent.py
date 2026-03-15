from __future__ import annotations

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import anthropic

from config.settings import Settings
from core.credits.tracker import CreditTracker
from core.error_handling.handlers import InsufficientCreditsError
from core.task_queue.schemas import AgentOutput, TaskPayload
from memory.learning_system.learning import LearningSystem
from memory.vector_memory.base import VectorStoreBase


class BaseAgent(ABC):
    agent_name: str = "base"

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
        self._client: anthropic.Anthropic | None = None

    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        return self._client

    @abstractmethod
    def run(self, task: TaskPayload) -> AgentOutput:
        """Execute the agent task and return structured output."""
        ...

    def _load_versioned_prompt(self, agent_name: str, version: str = "v1") -> str:
        path = Path(__file__).parent.parent / "prompts" / "prompt_versions" / version / f"{agent_name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"You are the {agent_name} agent for AI Product Studio."

    def _call_claude(
        self,
        messages: list[dict[str, Any]],
        system_prompt: str,
        max_tokens: int | None = None,
    ) -> tuple[str, int, int]:
        """
        Call Claude API. Returns (response_text, prompt_tokens, completion_tokens).
        If in fallback mode, returns a prompt-generation string instead.
        """
        max_tokens = max_tokens or self.settings.max_tokens_per_task

        if self.credit_tracker.fallback_mode:
            fallback = self._generate_fallback_prompt(messages, system_prompt)
            return fallback, 0, 0

        try:
            self.credit_tracker.check_and_deduct(max_tokens)
        except InsufficientCreditsError:
            fallback = self._generate_fallback_prompt(messages, system_prompt)
            return fallback, 0, 0

        start = time.monotonic()
        response = self.client.messages.create(
            model=self.settings.default_model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        prompt_tokens = response.usage.input_tokens
        completion_tokens = response.usage.output_tokens
        self.credit_tracker.record_actual_usage(prompt_tokens, completion_tokens)

        text = response.content[0].text if response.content else ""
        return text, prompt_tokens, completion_tokens

    def _generate_fallback_prompt(self, messages: list[dict], system_prompt: str) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
        )
        return (
            f"[FALLBACK MODE — credits exhausted]\n\n"
            f"System: {system_prompt[:200]}...\n\n"
            f"Task: {last_user[:500]}\n\n"
            f"Please run this prompt manually in Claude.ai to complete the task."
        )

    def _get_relevant_memory(self, query: str, project_id: str) -> list[str]:
        try:
            results = self.vector_store.search(f"project_{project_id}", query, top_k=3)
            return [r["text"] for r in results]
        except Exception:
            return []

    def _store_output(self, project_id: str, output_text: str, metadata: dict | None = None) -> None:
        try:
            import uuid
            self.vector_store.upsert(
                f"project_{project_id}",
                str(uuid.uuid4()),
                output_text,
                metadata,
            )
        except Exception:
            pass


def get_agent_for_type(
    agent_type: str,
    settings: Settings,
    credit_tracker: CreditTracker,
    vector_store: VectorStoreBase,
    learning_system: LearningSystem,
) -> BaseAgent:
    """Factory: resolve agent_type string → agent instance."""
    from agents.strategy_agent.agent import StrategyAgent
    from agents.research_agent.agent import ResearchAgent
    from agents.ux_agent.agent import UXAgent
    from agents.ui_agent.agent import UIAgent
    from agents.automation_agent.agent import AutomationAgent
    from agents.documentation_agent.agent import DocumentationAgent

    registry = {
        "strategy": StrategyAgent,
        "research": ResearchAgent,
        "ux": UXAgent,
        "ui": UIAgent,
        "automation": AutomationAgent,
        "documentation": DocumentationAgent,
    }
    klass = registry.get(agent_type)
    if klass is None:
        raise ValueError(f"Unknown agent_type: {agent_type!r}. Valid: {list(registry)}")
    return klass(
        settings=settings,
        credit_tracker=credit_tracker,
        vector_store=vector_store,
        learning_system=learning_system,
    )
