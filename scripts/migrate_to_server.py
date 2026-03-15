#!/usr/bin/env python3
"""
Migrate from local (SQLite + ChromaDB) to server (PostgreSQL + Qdrant).
Usage: python scripts/migrate_to_server.py [--dry-run]
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DRY_RUN = "--dry-run" in sys.argv


def log(msg: str) -> None:
    prefix = "[DRY RUN] " if DRY_RUN else ""
    print(f"{prefix}{msg}")


async def migrate_sqlite_to_postgres(local_db_url: str, server_db_url: str) -> None:
    log(f"SQLite → PostgreSQL: {local_db_url} → {server_db_url}")
    if DRY_RUN:
        log("Would migrate: projects, tasks, credit_ledger, agent_logs tables.")
        return
    # In a real migration, use sqlalchemy to read from SQLite and insert to PostgreSQL
    # This is a simplified version
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy import text

    src_engine = create_async_engine(local_db_url)
    dst_engine = create_async_engine(server_db_url)

    tables = ["projects", "tasks", "credit_ledger", "agent_logs"]
    for table in tables:
        async with src_engine.connect() as src_conn:
            result = await src_conn.execute(text(f"SELECT * FROM {table}"))
            rows = result.fetchall()
            cols = result.keys()
        if rows:
            async with dst_engine.begin() as dst_conn:
                for row in rows:
                    values = dict(zip(cols, row))
                    placeholders = ", ".join(f":{k}" for k in values)
                    col_names = ", ".join(values.keys())
                    await dst_conn.execute(
                        text(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"),
                        values,
                    )
            log(f"  Migrated {len(rows)} rows from {table}")

    await src_engine.dispose()
    await dst_engine.dispose()


def migrate_chroma_to_qdrant(chroma_path: str, qdrant_url: str) -> None:
    log(f"ChromaDB → Qdrant: {chroma_path} → {qdrant_url}")
    if DRY_RUN:
        log("Would migrate all ChromaDB collections to Qdrant.")
        return
    try:
        import chromadb
        from memory.vector_memory.qdrant_store import QdrantStore

        client = chromadb.PersistentClient(path=chroma_path)
        qdrant = QdrantStore(url=qdrant_url)
        for collection in client.list_collections():
            col = client.get_collection(collection.name)
            result = col.get(include=["documents", "metadatas"])
            for i, doc_id in enumerate(result["ids"]):
                text = result["documents"][i] if result["documents"] else ""
                meta = result["metadatas"][i] if result["metadatas"] else {}
                qdrant.upsert(collection.name, doc_id, text, meta)
            log(f"  Migrated collection: {collection.name} ({len(result['ids'])} docs)")
    except Exception as e:
        log(f"  ChromaDB → Qdrant migration error: {e}")


def migrate_project_files(src_path: str, dst_path: str) -> None:
    import shutil
    log(f"Project files: {src_path} → {dst_path}")
    if DRY_RUN:
        src = Path(src_path)
        if src.exists():
            count = sum(1 for _ in src.rglob("*"))
            log(f"  Would copy {count} files/dirs.")
        return
    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    log("  Project files copied.")


async def main() -> None:
    from config.settings import get_settings
    settings = get_settings()

    if settings.is_server:
        log("Already in server mode. Nothing to migrate.")
        return

    # Target server settings from env overrides
    server_db_url = "postgresql+asyncpg://studio:studio_pass@localhost:5432/studio"
    qdrant_url = "http://localhost:6333"
    server_projects_path = "/app/projects"

    log("=== AI Product Studio: Local → Server Migration ===")
    await migrate_sqlite_to_postgres(settings.database_url, server_db_url)
    migrate_chroma_to_qdrant(settings.chroma_path, qdrant_url)
    migrate_project_files(str(settings.projects_path), server_projects_path)
    log("=== Migration complete ===")


if __name__ == "__main__":
    asyncio.run(main())
