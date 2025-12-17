# Fix Database Encoding
$ErrorActionPreference = "Stop"
Write-Host "Starting Database Encoding Fix..." -ForegroundColor Cyan

# 1. Load Cloud Config
$envFile = ".env.cloud"
if (-not (Test-Path $envFile)) {
    Write-Host "Error: .env.cloud not found!" -ForegroundColor Red
    exit 1
}

$CLOUD_DB_URL = ""
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^DATABASE_URL=(.+)$') {
        $CLOUD_DB_URL = $matches[1].Trim()
        $CLOUD_DB_URL = $CLOUD_DB_URL -replace 'postgresql\+asyncpg://', 'postgresql://'
        $CLOUD_DB_URL = $CLOUD_DB_URL -replace 'ssl=require', 'sslmode=require'
    }
}

if (-not $CLOUD_DB_URL) {
    Write-Host "Error: DATABASE_URL not found!" -ForegroundColor Red
    exit 1
}

# 2. Dump Local DB
Write-Host "Dumping local database (Internal)..." -ForegroundColor Cyan
docker exec dev-db-1 pg_dump -U postgres tamozh_db --clean --if-exists --no-owner --no-privileges --file=/tmp/dump_utf8.sql

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to dump local database!" -ForegroundColor Red
    exit 1
}

# 3. Copy Dump to Host
Write-Host "Copying dump to host..." -ForegroundColor Cyan
docker cp dev-db-1:/tmp/dump_utf8.sql "$PSScriptRoot/dump_utf8.sql"

# 4. Restore to Cloud DB
Write-Host "Restoring to Cloud DB (Neon)..." -ForegroundColor Cyan
$dumpPath = Join-Path $PSScriptRoot "dump_utf8.sql"
docker run --rm -v "${dumpPath}:/dump.sql" postgres psql $CLOUD_DB_URL -f /dump.sql

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to restore to Cloud DB!" -ForegroundColor Red
} else {
    Write-Host "Database restored successfully with UTF-8!" -ForegroundColor Green
}

# Cleanup
if (Test-Path $dumpPath) {
    Remove-Item $dumpPath
}
docker exec dev-db-1 rm /tmp/dump_utf8.sql

Write-Host "Fix Complete!" -ForegroundColor Green
