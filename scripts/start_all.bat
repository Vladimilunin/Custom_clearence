@echo off
cd /d "%~dp0.."
echo Starting Database...
docker-compose up db -d

echo Starting Backend...
start "Backend" cmd /k "cd backend && uvicorn app.main:app --reload"

echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo All services started!
pause
