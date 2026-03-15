from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from core.database import create_tables, init_engine
from core.observability.logger import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging()
    settings.ensure_dirs()
    init_engine(settings)
    await create_tables()
    yield
    # Cleanup on shutdown (if needed)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Product Studio",
        description="Multi-agent AI product studio orchestrated by OpenClaw Jimmy",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from api.routers import projects, tasks, credits, ingest
    app.include_router(projects.router, prefix="/projects", tags=["projects"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    app.include_router(credits.router, prefix="/credits", tags=["credits"])
    app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "ai-product-studio"}

    return app


app = create_app()
