from __future__ import annotations

AGENT_TOOL_MATRIX: dict[str, set[str]] = {
    "strategy":      {"vector_store", "project_store", "learning"},
    "research":      {"vector_store", "project_store", "learning", "ingestion"},
    "ux":            {"vector_store", "project_store", "learning", "uxpilot"},
    "ui":            {"vector_store", "project_store", "learning", "uxpilot", "figma"},
    "automation":    {"vector_store", "project_store", "learning", "claude_code"},
    "documentation": {"vector_store", "project_store", "learning"},
    "manager":       {"vector_store", "project_store", "learning", "uxpilot", "figma", "claude_code", "ingestion"},
}


class PermissionDeniedError(Exception):
    pass


def check_permission(agent_type: str, tool_name: str) -> None:
    allowed = AGENT_TOOL_MATRIX.get(agent_type, set())
    if tool_name not in allowed:
        raise PermissionDeniedError(
            f"Agent '{agent_type}' is not permitted to use tool '{tool_name}'. "
            f"Allowed tools: {sorted(allowed)}"
        )


def get_allowed_tools(agent_type: str) -> set[str]:
    return AGENT_TOOL_MATRIX.get(agent_type, set()).copy()
