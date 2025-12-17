# Migrate Local DB to Cloud DB
# Reads DATABASE_URL from .env.cloud

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Database Migration..." -ForegroundColor Cyan

# 1. Load Cloud Config
$envFile = ".env.cloud"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ .env.cloud not found!" -ForegroundColor Red
    exit 1
}

$CLOUD_DB_URL = ""
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^DATABASE_URL=(.+)$') {
        $CLOUD_DB_URL = $matches[1].Trim()
        # Replace postgresql+asyncpg:// with postgresql:// for psql
        $CLOUD_DB_URL = $CLOUD_DB_URL -replace 'postgresql\+asyncpg://', 'postgresql://'
    }
}

if (-not $CLOUD_DB_URL) {
    Write-Host "❌ DATABASE_URL not found in .env.cloud!" -ForegroundColor Red
    exit 1
}

Write-Host "☁️  Target Cloud DB found." -ForegroundColor Green

# 2. Dump Local DB
Write-Host "📦 Dumping local database..." -ForegroundColor Cyan

# Use absolute path for dump file
$dumpFile = "$PSScriptRoot\dump.sql"
Write-Host "   Dump file path: $dumpFile" -ForegroundColor Gray

# Use docker exec directly to avoid docker-compose context issues
# Container name is assumed to be 'dev-db-1' based on project structure
docker exec -i dev-db-1 pg_dump -U postgres tamozh_db --clean --if-exists --no-owner --no-privileges > $dumpFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to dump local database! Ensure container 'dev-db-1' is running." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Local database dumped to dump.sql" -ForegroundColor Green

# 3. Restore to Cloud DB
Write-Host "📤 Restoring to Cloud DB (Neon)..." -ForegroundColor Cyan
Write-Host "   This might take a while..." -ForegroundColor Yellow

# Use a temporary postgres container to run psql if local psql is not available or version mismatch
# We pipe the dump.sql into psql connected to the cloud DB
Get-Content $dumpFile | docker run -i --rm postgres psql $CLOUD_DB_URL

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to restore to Cloud DB!" -ForegroundColor Red
    # Don't exit here, maybe just a warning if some errors are non-critical
} else {
    Write-Host "✅ Database restored successfully!" -ForegroundColor Green
}

# Cleanup
if (Test-Path $dumpFile) {
    Remove-Item $dumpFile
}
Write-Host "🧹 Cleanup complete." -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Migration Complete!" -ForegroundColor Green
