@echo off
cd /d "%~dp0.."
setlocal

echo ==========================================
echo Starting Service Deployment
echo ==========================================

:: Check for Docker
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed or not in PATH.
    echo Please install Docker Desktop and try again.
    pause
    exit /b 1
)

:: 1. Start Database Container
echo.
echo [Step 1/3] Starting Database container...
docker-compose up -d db
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to start database container.
    pause
    exit /b 1
)

echo Waiting for database to initialize (10 seconds)...
timeout /t 10 /nobreak >nul

:: 2. Restore Database
echo.
echo [Step 2/3] Restoring Database...
:: Find the latest backup file
for /f "delims=" %%F in ('dir /b /o-n backups\backup_*.sql') do set LATEST_BACKUP=backups\%%F
if "%LATEST_BACKUP%"=="" (
    echo Warning: No backup file found in backups\ directory. Skipping restore.
) else (
    echo Found latest backup: %LATEST_BACKUP%
    call "%~dp0restore_db.bat" "%LATEST_BACKUP%"
)

:: 2.1 Run Migrations (Ensure DB schema is up to date)
echo.
echo [Step 2.1/3] Running Database Migrations...
docker-compose exec -T backend alembic upgrade head
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to run migrations. Please check backend logs.
)

:: 3. Build and Start All Services
echo.
echo [Step 3/3] Building and Starting Application Services...
docker-compose up -d --build
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to start services.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Deployment Completed Successfully!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000/docs
echo ==========================================
pause
