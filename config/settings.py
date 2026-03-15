from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Deployment
    deployment_mode: str = "local"  # "local" | "server"

    # Anthropic
    anthropic_api_key: str = ""
    default_model: str = "claude-sonnet-4-6"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/studio.db"

    # Vector DB
    vector_db_type: str = "chroma"  # "chroma" | "qdrant"
    chroma_path: str = "./data/chroma"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # Paths
    projects_base_path: str = "./projects"

    # Credits / limits
    credits_total: int = 1000
    max_tokens_per_task: int = 8000
    max_tokens_per_project: int = 100000

    # Tool APIs
    uxpilot_api_key: str = ""
    figma_api_key: str = ""
    notion_api_key: str = ""
    google_drive_credentials_path: str = ""

    @property
    def projects_path(self) -> Path:
        return Path(self.projects_base_path).resolve()

    @property
    def is_local(self) -> bool:
        return self.deployment_mode == "local"

    @property
    def is_server(self) -> bool:
        return self.deployment_mode == "server"

    def ensure_dirs(self) -> None:
        """Create required runtime directories."""
        self.projects_path.mkdir(parents=True, exist_ok=True)
        Path("./data").mkdir(parents=True, exist_ok=True)
        Path("./logs").mkdir(parents=True, exist_ok=True)
        if self.is_local:
            Path(self.chroma_path).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env_file = os.environ.get("ENV_FILE", ".env.local")
    return Settings(_env_file=env_file)
