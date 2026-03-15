from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import Settings


class LearningSystem:
    """Records and retrieves per-agent lessons from past projects."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_path = settings.projects_path

    def _learning_path(self, project_id: str) -> Path:
        d = self.base_path / project_id
        d.mkdir(parents=True, exist_ok=True)
        return d / "learning.md"

    def record_lesson(self, project_id: str, agent_type: str, lesson: str) -> None:
        path = self._learning_path(project_id)
        timestamp = datetime.utcnow().isoformat()
        entry = f"\n## [{timestamp}] {agent_type}\n{lesson}\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(entry)

    def load_lessons(self, agent_type: str, max_lessons: int = 10) -> list[str]:
        """Load the most recent lessons for a given agent type across all projects."""
        lessons: list[tuple[datetime, str]] = []
        if not self.base_path.exists():
            return []
        for learning_file in self.base_path.glob("*/learning.md"):
            content = learning_file.read_text(encoding="utf-8")
            for block in content.split("\n## "):
                if not block.strip():
                    continue
                first_line = block.split("\n")[0]
                if agent_type in first_line:
                    try:
                        ts_str = first_line.strip("[]").split("]")[0].strip("[")
                        ts = datetime.fromisoformat(ts_str)
                    except Exception:
                        ts = datetime.min
                    text = "\n".join(block.split("\n")[1:]).strip()
                    lessons.append((ts, text))
        lessons.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in lessons[:max_lessons]]
