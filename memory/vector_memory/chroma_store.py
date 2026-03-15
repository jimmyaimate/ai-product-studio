from __future__ import annotations

from typing import Any

from memory.vector_memory.base import VectorStoreBase


class ChromaStore(VectorStoreBase):
    """ChromaDB vector store (local mode)."""

    def __init__(self, path: str):
        import chromadb
        self._client = chromadb.PersistentClient(path=path)
        self._collections: dict[str, Any] = {}

    def _get_or_create(self, collection: str):
        if collection not in self._collections:
            self._collections[collection] = self._client.get_or_create_collection(
                name=collection,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[collection]

    def upsert(self, collection: str, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        col = self._get_or_create(collection)
        col.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def search(self, collection: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        col = self._get_or_create(collection)
        results = col.query(query_texts=[query], n_results=min(top_k, col.count() or 1))
        output = []
        for i, doc_id in enumerate(results["ids"][0]):
            output.append({
                "id": doc_id,
                "text": results["documents"][0][i],
                "score": 1 - results["distances"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            })
        return output

    def delete(self, collection: str, doc_id: str) -> None:
        col = self._get_or_create(collection)
        col.delete(ids=[doc_id])

    def delete_collection(self, collection: str) -> None:
        self._client.delete_collection(name=collection)
        self._collections.pop(collection, None)
