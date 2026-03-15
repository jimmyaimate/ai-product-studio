from __future__ import annotations

import time
import functools
import logging
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)


class AgentError(Exception):
    """Base error for agent failures."""
    def __init__(self, message: str, agent_type: str = "", task_id: str = ""):
        super().__init__(message)
        self.agent_type = agent_type
        self.task_id = task_id


class InsufficientCreditsError(AgentError):
    """Raised when token budget is exhausted."""


class ToolError(AgentError):
    """Raised when an external tool call fails."""
    def __init__(self, message: str, tool_name: str = "", **kwargs):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator: retry on exception with exponential backoff."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except InsufficientCreditsError:
                    raise
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s. Retrying in %.1fs",
                            attempt + 1, max_retries, func.__name__, exc, delay,
                        )
                        time.sleep(delay)
            raise last_exc
        return wrapper  # type: ignore
    return decorator
