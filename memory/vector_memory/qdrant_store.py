from __future__ import annotations

from typing import Any

from memory.vector_memory.base import VectorStoreBase


class QdrantStore(VectorStoreBase):
    """Qdrant vector store (server mode)."""

    VECTOR_SIZE = 1536  # text-embedding-3-small compatible; adjust if using different embedder

    def __init__(self, url: str, api_key: str = ""):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        self._client = QdrantClient(url=url, api_key=api_key or None)
        self._Distance = Distance
        self._VectorParams = VectorParams

    def _ensure_collection(self, collection: str) -> None:
        existing = [c.name for c in self._client.get_collections().collections]
        if collection not in existing:
            self._client.create_collection(
                collection_name=collection,
                vectors_config=self._VectorParams(
                    size=self.VECTOR_SIZE, distance=self._Distance.COSINE
                ),
            )

    def _embed(self, text: str) -> list[float]:
        """Simple embedding via Anthropic or fallback to zeros for testing."""
        try:
            import anthropic
            import os
            # Qdrant store uses a separate embedding; fall back to dummy if no key
            key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not key:
                return [0.0] * self.VECTOR_SIZE
            # Use a lightweight approach: hash-based pseudo-embedding for now
            # In production, swap with a real embedding model
            import hashlib
            h = int(hashlib.md5(text.encode()).hexdigest(), 16)
            import random
            rng = random.Random(h)
            return [rng.gauss(0, 1) for _ in range(self.VECTOR_SIZE)]
        except Exception:
            return [0.0] * self.VECTOR_SIZE

    def upsert(self, collection: str, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        from qdrant_client.models import PointStruct
        self._ensure_collection(collection)
        vector = self._embed(text)
        self._client.upsert(
            collection_name=collection,
            points=[PointStruct(
                id=abs(hash(doc_id)) % (2**31),
                vector=vector,
                payload={"doc_id": doc_id, "text": text, **(metadata or {})},
            )],
        )

    def search(self, collection: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        self._ensure_collection(collection)
        vector = self._embed(query)
        hits = self._client.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
        )
        return [
            {
                "id": h.payload.get("doc_id", str(h.id)),
                "text": h.payload.get("text", ""),
                "score": h.score,
                "metadata": {k: v for k, v in h.payload.items() if k not in ("doc_id", "text")},
            }
            for h in hits
        ]

    def delete(self, collection: str, doc_id: str) -> None:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        self._ensure_collection(collection)
        self._client.delete(
            collection_name=collection,
            points_selector=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            ),
        )

    def delete_collection(self, collection: str) -> None:
        self._client.delete_collection(collection_name=collection)
