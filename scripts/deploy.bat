@echo off
REM deploy.bat — pull latest code and restart backend services (Windows)

cd /d "%~dp0.."

echo.
echo === AI Product Studio - Deploy ===
echo.

REM 1. Pull latest
echo [1/4] Pulling latest from GitHub...
git pull

REM 2. Install deps
echo [2/4] Installing dependencies...
pip install -r requirements.txt --quiet

REM 3. Setup
echo [3/4] Running setup...
python scripts/setup.py

REM 4. Restart services
echo [4/4] Restarting services...

REM Kill existing processes
taskkill /F /FI "WINDOWTITLE eq celery*" 2>nul
taskkill /F /FI "WINDOWTITLE eq uvicorn*" 2>nul

timeout /t 2 /nobreak >nul

REM Start Celery in new window
start "celery" cmd /k "celery -A core.task_queue.celery_app worker --loglevel=info -Q agents"

REM Start FastAPI in new window
start "uvicorn" cmd /k "python main.py server"

echo.
echo === Deploy complete ===
echo   API: http://localhost:8000
echo   Two new windows opened for Celery and FastAPI
echo.
