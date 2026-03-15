#!/usr/bin/env python3
"""Alembic migration wrapper that works on both SQLite and PostgreSQL."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_alembic(*args: str) -> int:
    return subprocess.run(["alembic", *args], cwd=str(Path(__file__).parent.parent)).returncode


def main() -> None:
    from config.settings import get_settings
    settings = get_settings()
    print(f"[migrate] Running against: {settings.database_url}")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    target = sys.argv[2] if len(sys.argv) > 2 else "head"
    rc = run_alembic(cmd, target)
    sys.exit(rc)


if __name__ == "__main__":
    main()
