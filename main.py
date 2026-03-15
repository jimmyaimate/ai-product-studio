#!/usr/bin/env python3
"""
AI Product Studio — CLI entrypoint.

Usage:
  python main.py start-project --template saas --brief "Build a task management SaaS"
  python main.py status --project-id <uuid>
  python main.py server
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

app = typer.Typer(name="ai-product-studio", help="Multi-agent AI product studio — OpenClaw Jimmy")
console = Console()


@app.command("start-project")
def start_project(
    brief: str = typer.Option(..., "--brief", "-b", help="Product brief / idea description"),
    template: str = typer.Option("saas", "--template", "-t", help="Template: saas | landing_page | dashboard | marketplace"),
    sync: bool = typer.Option(False, "--sync", help="Run synchronously (wait for all agents to complete)"),
):
    """Kick off a new AI product studio project."""
    from config.settings import get_settings
    from core.credits.tracker import CreditTracker
    from core.database import create_tables, init_engine
    from core.observability.logger import configure_logging
    from memory.learning_system.learning import LearningSystem
    from memory.vector_memory.factory import get_vector_store
    from agents.manager_agent.jimmy import OpenClawJimmy

    configure_logging()
    settings = get_settings()
    settings.ensure_dirs()
    init_engine(settings)
    asyncio.run(create_tables())

    credit_tracker = CreditTracker(settings)
    vector_store = get_vector_store(settings)
    learning_system = LearningSystem(settings)

    jimmy = OpenClawJimmy(
        settings=settings,
        credit_tracker=credit_tracker,
        vector_store=vector_store,
        learning_system=learning_system,
    )

    console.print(Panel(
        f"[bold cyan]OpenClaw Jimmy[/] is starting your project\n\n"
        f"[yellow]Brief:[/] {brief[:200]}\n"
        f"[yellow]Template:[/] {template}\n"
        f"[yellow]Mode:[/] {'synchronous' if sync else 'async (Celery)'}",
        title="AI Product Studio",
        border_style="cyan",
    ))

    if sync:
        result = jimmy.handle_project(brief, template=template)
        console.print(Panel(JSON(str(result).replace("'", '"')), title="Project Complete", border_style="green"))
    else:
        import uuid
        project_id = str(uuid.uuid4())
        celery_id = jimmy.dispatch_task("research", {"brief": brief, "template": template}, project_id=project_id)
        console.print(f"\n[green]✓[/] Project dispatched!")
        console.print(f"  Project ID : [bold]{project_id}[/]")
        console.print(f"  Celery task: [dim]{celery_id}[/]")
        console.print(f"\n  Check status: [cyan]python main.py status --project-id {project_id}[/]")
        console.print(f"  Or via API  : [cyan]GET http://localhost:8000/projects/{project_id}/status[/]")


@app.command("status")
def project_status(
    project_id: str = typer.Option(..., "--project-id", "-p", help="Project UUID"),
):
    """Check the status of a running project."""
    from config.settings import get_settings
    from core.credits.tracker import CreditTracker
    from memory.learning_system.learning import LearningSystem
    from memory.vector_memory.factory import get_vector_store
    from agents.manager_agent.jimmy import OpenClawJimmy

    settings = get_settings()
    jimmy = OpenClawJimmy(
        settings=settings,
        credit_tracker=CreditTracker(settings),
        vector_store=get_vector_store(settings),
        learning_system=LearningSystem(settings),
    )
    status = jimmy.get_project_status(project_id)
    console.print_json(data=status)


@app.command("server")
def run_server(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
    reload: bool = typer.Option(False, "--reload"),
):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run("api.main:app", host=host, port=port, reload=reload)


@app.command("setup")
def run_setup():
    """Run first-time setup (create DB tables, directories)."""
    asyncio.run(_async_setup())


async def _async_setup():
    from config.settings import get_settings
    from core.database import create_tables, init_engine
    from core.observability.logger import configure_logging

    configure_logging()
    settings = get_settings()
    settings.ensure_dirs()
    init_engine(settings)
    await create_tables()
    console.print("[green]✓[/] Setup complete.")


if __name__ == "__main__":
    app()
