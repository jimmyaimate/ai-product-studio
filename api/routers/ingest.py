from __future__ import annotations

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import Any
import tempfile
import os

from api.deps import SettingsDep, VectorStoreDep

router = APIRouter()


class URLIngestRequest(BaseModel):
    url: str
    project_id: str


class NotionIngestRequest(BaseModel):
    page_url: str
    project_id: str


@router.post("/pdf")
async def ingest_pdf(
    project_id: str,
    file: UploadFile = File(...),
    settings: SettingsDep = None,
    vector_store: VectorStoreDep = None,
) -> dict[str, Any]:
    from tools.ingestion.ingestion_service import IngestionService
    service = IngestionService(settings, vector_store)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        return service.ingest_pdf(tmp_path, project_id)
    finally:
        os.unlink(tmp_path)


@router.post("/url")
async def ingest_url(
    req: URLIngestRequest,
    settings: SettingsDep,
    vector_store: VectorStoreDep,
) -> dict[str, Any]:
    from tools.ingestion.ingestion_service import IngestionService
    service = IngestionService(settings, vector_store)
    return service.ingest_url(req.url, req.project_id)


@router.post("/notion")
async def ingest_notion(
    req: NotionIngestRequest,
    settings: SettingsDep,
    vector_store: VectorStoreDep,
) -> dict[str, Any]:
    from tools.ingestion.ingestion_service import IngestionService
    service = IngestionService(settings, vector_store)
    return service.ingest_notion(req.page_url, req.project_id)
