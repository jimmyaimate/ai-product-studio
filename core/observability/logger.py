from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog


def configure_logging(log_level: str = "INFO", log_dir: str = "./logs") -> None:
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if sys.stdout.isatty() else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(log_level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

    # Also configure stdlib logging to propagate to structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(log_level),
    )

    file_handler = logging.FileHandler(Path(log_dir) / "studio.log", encoding="utf-8")
    file_handler.setLevel(logging.getLevelName(log_level))
    logging.getLogger().addHandler(file_handler)


def get_logger(name: str):
    return structlog.get_logger(name)


def log_agent_call(
    agent_type: str,
    task_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    error: str | None = None,
    fallback_mode: bool = False,
) -> None:
    logger = get_logger("agent")
    logger.info(
        "agent_call",
        agent_type=agent_type,
        task_id=task_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        latency_ms=latency_ms,
        error=error,
        fallback_mode=fallback_mode,
    )
