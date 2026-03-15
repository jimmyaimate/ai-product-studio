#!/usr/bin/env python3
"""First-run initializer: create DB tables, seed credits, create projects dir."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def main() -> None:
    from config.settings import get_settings
    from core.database import create_tables, init_engine
    from core.observability.logger import configure_logging

    configure_logging()
    settings = get_settings()
    settings.ensure_dirs()

    print(f"[setup] Deployment mode: {settings.deployment_mode}")
    print(f"[setup] Database: {settings.database_url}")
    print(f"[setup] Vector DB: {settings.vector_db_type}")
    print(f"[setup] Projects path: {settings.projects_path}")

    init_engine(settings)
    await create_tables()
    print("[setup] Database tables created.")

    # Create projects dir
    settings.projects_path.mkdir(parents=True, exist_ok=True)
    (settings.projects_path / ".gitkeep").touch(exist_ok=True)
    print(f"[setup] Projects directory ready: {settings.projects_path}")

    print("[setup] ✓ Setup complete.")


if __name__ == "__main__":
    asyncio.run(main())
