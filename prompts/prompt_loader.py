from __future__ import annotations

import re
from pathlib import Path


PROMPTS_BASE = Path(__file__).parent / "prompt_versions"


def _list_versions() -> list[str]:
    if not PROMPTS_BASE.exists():
        return []
    dirs = sorted(
        [d.name for d in PROMPTS_BASE.iterdir() if d.is_dir() and re.match(r"v\d+", d.name)],
        key=lambda x: int(x[1:]),
    )
    return dirs


def load_prompt(agent_name: str, version: str | None = None) -> str:
    """Load a versioned system prompt. Uses latest version if version=None."""
    versions = _list_versions()
    if not versions:
        return f"You are the {agent_name} agent for AI Product Studio."

    target_version = version or versions[-1]
    path = PROMPTS_BASE / target_version / f"{agent_name}.md"

    if not path.exists():
        return f"You are the {agent_name} agent for AI Product Studio."

    content = path.read_text(encoding="utf-8")
    # Strip YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()


def get_latest_version() -> str | None:
    versions = _list_versions()
    return versions[-1] if versions else None
