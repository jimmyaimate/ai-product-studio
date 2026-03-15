#!/usr/bin/env bash
# deploy.sh — pull latest code and restart backend services
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo ""
echo "=== AI Product Studio — Deploy ==="
echo ""

# 1. Pull latest
echo "[1/4] Pulling latest from GitHub..."
git pull

# 2. Install any new Python deps
echo "[2/4] Installing dependencies..."
pip install -r requirements.txt --quiet

# 3. Run setup (creates tables if schema changed, safe to re-run)
echo "[3/4] Running setup..."
python scripts/setup.py

# 4. Restart backend services
echo "[4/4] Restarting services..."

# Kill existing celery + uvicorn if running
pkill -f "celery.*ai_product_studio" 2>/dev/null && echo "  Stopped Celery" || echo "  Celery was not running"
pkill -f "uvicorn.*api.main" 2>/dev/null && echo "  Stopped Uvicorn" || echo "  Uvicorn was not running"

sleep 2

# Start Celery worker in background
nohup celery -A core.task_queue.celery_app worker --loglevel=info -Q agents \
  > logs/celery.log 2>&1 &
echo "  Celery started (logs/celery.log)"

# Start FastAPI in background
nohup python main.py server \
  > logs/api.log 2>&1 &
echo "  FastAPI started (logs/api.log)"

echo ""
echo "=== Deploy complete ==="
echo "  API:    http://localhost:8000"
echo "  Logs:   tail -f logs/api.log"
echo "          tail -f logs/celery.log"
echo ""
