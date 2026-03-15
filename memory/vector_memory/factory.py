from __future__ import annotations

from config.settings import Settings
from memory.vector_memory.base import VectorStoreBase


def get_vector_store(settings: Settings) -> VectorStoreBase:
    if settings.vector_db_type == "qdrant":
        from memory.vector_memory.qdrant_store import QdrantStore
        return QdrantStore(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    else:
        from memory.vector_memory.chroma_store import ChromaStore
        return ChromaStore(path=settings.chroma_path)
