# AI Product Studio

Multi-agent AI product studio orchestrated by **OpenClaw Jimmy**. Automates product strategy, UX/UI design, research, and MVP specifications using Claude (claude-sonnet-4-6).

## Quick Start

### Local Development

```bash
# 1. Clone and enter directory
git clone <repo> ai-product-studio && cd ai-product-studio

# 2. Copy and configure environment
cp .env.example .env.local
# Edit .env.local — add your ANTHROPIC_API_KEY

# 3. Install dependencies
pip install -e .

# 4. Run setup (creates DB, directories)
python scripts/setup.py

# 5. Start Redis (required for Celery)
docker run -d -p 6379:6379 redis:7-alpine

# 6. Start Celery worker (in a separate terminal)
celery -A core.task_queue.celery_app worker --loglevel=info -Q agents

# 7. Start a project
python main.py start-project --template saas --brief "Build a task management SaaS for remote teams"
```

### Docker (All-in-one)

```bash
# Local mode (SQLite + ChromaDB)
bash scripts/start_local.sh

# Server mode (PostgreSQL + Qdrant)
bash scripts/start_server.sh
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DEPLOYMENT_MODE` | `local` or `server` | `local` |
| `ANTHROPIC_API_KEY` | Anthropic API key | required |
| `DEFAULT_MODEL` | Claude model ID | `claude-sonnet-4-6` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `DATABASE_URL` | SQLAlchemy async URL | SQLite local |
| `VECTOR_DB_TYPE` | `chroma` or `qdrant` | `chroma` |
| `PROJECTS_BASE_PATH` | Project files directory | `./projects` |
| `CREDITS_TOTAL` | Total credit budget | `1000` |
| `MAX_TOKENS_PER_TASK` | Per-task token limit | `8000` |
| `MAX_TOKENS_PER_PROJECT` | Per-project token budget | `100000` |

## Agents

| Agent | Responsibility |
|---|---|
| **OpenClaw Jimmy** | Manager — orchestrates the full pipeline |
| **Research** | User personas, competitor analysis, market sizing |
| **Strategy** | Business model, GTM, feature prioritization, roadmap |
| **UX** | User flows, information architecture, wireframe prompts |
| **UI** | Design system, component specs, Figma prompts |
| **Automation** | Integration specs, API design, Claude Code tasks |
| **Documentation** | PRD, README, onboarding guides, ADRs |

## Templates

- `saas` — SaaS dashboard with auth, billing, teams
- `landing_page` — High-converting marketing page
- `dashboard` — Analytics/admin dashboard
- `marketplace` — Two-sided marketplace

## API

```
POST   /projects                    — Start a project
GET    /projects/{id}               — Get project + outputs
GET    /projects/{id}/status        — Poll progress
GET    /tasks/{id}                  — Check Celery task
POST   /tasks/{id}/retry            — Retry failed task
GET    /credits                     — Credit usage
POST   /credits/reload              — Reset credit tracker
POST   /ingest/pdf                  — Ingest PDF document
POST   /ingest/url                  — Ingest web URL
POST   /ingest/notion               — Ingest Notion page
```

## Migration: Local → Server

```bash
# Validate migration path (no side effects)
python scripts/migrate_to_server.py --dry-run

# Execute migration
python scripts/migrate_to_server.py
```
