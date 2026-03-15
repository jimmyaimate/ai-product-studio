from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class VectorStoreBase(ABC):
    """Abstract interface for vector stores."""

    @abstractmethod
    def upsert(self, collection: str, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Embed and store a document."""
        ...

    @abstractmethod
    def search(self, collection: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Semantic search; returns list of {id, text, score, metadata}."""
        ...

    @abstractmethod
    def delete(self, collection: str, doc_id: str) -> None:
        """Remove a document by ID."""
        ...

    @abstractmethod
    def delete_collection(self, collection: str) -> None:
        """Drop an entire collection."""
        ...
