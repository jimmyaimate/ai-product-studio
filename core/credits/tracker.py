from __future__ import annotations

import logging
from pathlib import Path

from config.settings import Settings
from core.error_handling.handlers import InsufficientCreditsError

logger = logging.getLogger(__name__)


class CreditTracker:
    """Tracks token usage and enforces project credit limits."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.credits_total = settings.credits_total
        self.max_tokens_per_project = settings.max_tokens_per_project
        self._tokens_used: int = 0
        self.fallback_mode: bool = False

    @property
    def tokens_used(self) -> int:
        return self._tokens_used

    @property
    def tokens_remaining(self) -> int:
        return max(0, self.max_tokens_per_project - self._tokens_used)

    def check_and_deduct(self, tokens_estimate: int) -> None:
        """Raise InsufficientCreditsError if over budget, else deduct."""
        if self.fallback_mode:
            return
        if self._tokens_used + tokens_estimate > self.max_tokens_per_project:
            self.switch_to_fallback_mode()
            raise InsufficientCreditsError(
                f"Token budget exhausted: {self._tokens_used}/{self.max_tokens_per_project} used."
            )
        self._tokens_used += tokens_estimate
        logger.debug("Credits used: %d / %d", self._tokens_used, self.max_tokens_per_project)

    def record_actual_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Call after API response to correct the estimate."""
        actual = prompt_tokens + completion_tokens
        # Already deducted an estimate; just update the running total to actual
        self._tokens_used = max(self._tokens_used, actual)

    def switch_to_fallback_mode(self) -> None:
        """Stop making API calls; agents generate manual prompts instead."""
        if not self.fallback_mode:
            logger.warning("Switching to fallback mode (credits exhausted).")
        self.fallback_mode = True

    def reset(self) -> None:
        self._tokens_used = 0
        self.fallback_mode = False

    def summary(self) -> dict:
        return {
            "tokens_used": self._tokens_used,
            "tokens_remaining": self.tokens_remaining,
            "max_tokens": self.max_tokens_per_project,
            "fallback_mode": self.fallback_mode,
        }
