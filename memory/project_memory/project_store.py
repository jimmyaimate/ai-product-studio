from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import Settings


class ProjectStore:
    """CRUD for project context stored as JSON files alongside relational records."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_path = settings.projects_path

    def _project_dir(self, project_id: str) -> Path:
        d = self.base_path / project_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_context(self, project_id: str, key: str, data: Any) -> None:
        path = self._project_dir(project_id) / f"{key}.json"
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def load_context(self, project_id: str, key: str) -> Any | None:
        path = self._project_dir(project_id) / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def save_agent_output(self, project_id: str, agent_type: str, output: dict[str, Any]) -> None:
        timestamped_key = f"output_{agent_type}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
        self.save_context(project_id, timestamped_key, output)
        # Also overwrite the "latest" snapshot
        self.save_context(project_id, f"output_{agent_type}_latest", output)

    def load_latest_output(self, project_id: str, agent_type: str) -> dict[str, Any] | None:
        return self.load_context(project_id, f"output_{agent_type}_latest")

    def list_outputs(self, project_id: str) -> list[str]:
        d = self._project_dir(project_id)
        return [p.stem for p in d.glob("output_*.json")]

    def compile_all_outputs(self, project_id: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key in self.list_outputs(project_id):
            if key.endswith("_latest"):
                agent = key.replace("output_", "").replace("_latest", "")
                result[agent] = self.load_context(project_id, key)
        return result
