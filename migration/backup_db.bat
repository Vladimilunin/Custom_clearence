@echo off
cd /d "%~dp0.."
setlocal

echo Starting backup process...
python "%~dp0backup_remote.py"

if %ERRORLEVEL% EQU 0 (
    echo Backup created successfully!
) else (
    echo Error creating backup. Please ensure Docker Desktop is running.
)

endlocal
pause
