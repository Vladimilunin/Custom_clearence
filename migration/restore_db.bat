@echo off
cd /d "%~dp0.."
setlocal

if "%~1"=="" (
    echo Usage: restore_db.bat ^<backup_file^>
    echo Example: restore_db.bat backups\backup_2023-10-27_12-00.sql
    exit /b 1
)

set BACKUP_FILE=%~1

if not exist "%BACKUP_FILE%" (
    echo Error: Backup file not found: %BACKUP_FILE%
    exit /b 1
)

echo Restoring database from %BACKUP_FILE%...
echo WARNING: This will overwrite the current database!
:: set /p confirm="Are you sure? (y/n): "
:: if /i not "%confirm%"=="y" exit /b

:: Drop and recreate schema to ensure clean state (optional, but safer)
docker-compose exec -T db psql -U postgres -d tamozh_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

:: Restore
type "%BACKUP_FILE%" | docker-compose exec -T db psql -U postgres tamozh_db

if %ERRORLEVEL% EQU 0 (
    echo Database restored successfully!
) else (
    echo Error restoring database.
)

endlocal
pause
