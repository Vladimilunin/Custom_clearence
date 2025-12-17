@echo off
cd /d "%~dp0.."
setlocal

echo ==========================================
echo Starting Migration Archive Creation
echo ==========================================

:: 1. Backup Database
echo.
echo [Step 1/2] Backing up database...
call "%~dp0backup_db.bat"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Database backup failed!
    pause
    exit /b 1
)

:: 2. Archive Project
echo.
echo [Step 2/2] Archiving project files...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0archive_project.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Archiving failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Migration Archive Created Successfully!
echo ==========================================
pause
