from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import httpx

from config.settings import Settings
from memory.vector_memory.base import VectorStoreBase


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return [c for c in chunks if c.strip()]


class IngestionService:
    def __init__(self, settings: Settings, vector_store: VectorStoreBase):
        self.settings = settings
        self.vector_store = vector_store

    def _ingest_text(self, text: str, project_id: str, source: str) -> int:
        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            self.vector_store.upsert(
                collection=f"project_{project_id}",
                doc_id=str(uuid.uuid4()),
                text=chunk,
                metadata={"source": source, "chunk_index": i},
            )
        return len(chunks)

    def ingest_notion(self, page_url: str, project_id: str) -> dict[str, Any]:
        api_key = self.settings.notion_api_key
        if not api_key:
            return {"error": "NOTION_API_KEY not configured"}
        # Extract page_id from URL
        page_id = page_url.rstrip("/").split("-")[-1].replace("-", "")
        headers = {"Authorization": f"Bearer {api_key}", "Notion-Version": "2022-06-28"}
        with httpx.Client() as client:
            resp = client.get(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=headers)
            resp.raise_for_status()
        blocks = resp.json().get("results", [])
        text_parts = []
        for block in blocks:
            btype = block.get("type", "")
            content = block.get(btype, {})
            for rt in content.get("rich_text", []):
                text_parts.append(rt.get("plain_text", ""))
        full_text = "\n".join(text_parts)
        chunks = self._ingest_text(full_text, project_id, source=f"notion:{page_url}")
        return {"source": "notion", "chunks": chunks}

    def ingest_google_drive(self, file_id: str, project_id: str) -> dict[str, Any]:
        creds_path = self.settings.google_drive_credentials_path
        if not creds_path:
            return {"error": "GOOGLE_DRIVE_CREDENTIALS_PATH not configured"}
        try:
            from googleapiclient.discovery import build
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/drive.readonly"])
            service = build("drive", "v3", credentials=creds)
            content = service.files().export(fileId=file_id, mimeType="text/plain").execute()
            text = content.decode("utf-8") if isinstance(content, bytes) else str(content)
        except Exception as e:
            return {"error": str(e)}
        chunks = self._ingest_text(text, project_id, source=f"gdrive:{file_id}")
        return {"source": "gdrive", "chunks": chunks}

    def ingest_pdf(self, file_path: str, project_id: str) -> dict[str, Any]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            return {"error": str(e)}
        chunks = self._ingest_text(text, project_id, source=f"pdf:{Path(file_path).name}")
        return {"source": "pdf", "file": file_path, "chunks": chunks}

    def ingest_url(self, url: str, project_id: str) -> dict[str, Any]:
        try:
            from bs4 import BeautifulSoup
            with httpx.Client(follow_redirects=True, timeout=30) as client:
                resp = client.get(url)
                resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
        except Exception as e:
            return {"error": str(e)}
        chunks = self._ingest_text(text, project_id, source=f"url:{url}")
        return {"source": "url", "url": url, "chunks": chunks}
