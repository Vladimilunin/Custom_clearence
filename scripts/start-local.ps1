# Start local development environment with all services
# PowerShell version

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Starting Local Development Environment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Stop any existing containers
Write-Host "[1/5] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Start all services
Write-Host "[2/5] Starting Docker Compose services..." -ForegroundColor Cyan
docker-compose up -d --build

# Wait for all services to be healthy
Write-Host "[3/5] Waiting for services to be ready (this may take a minute)..." -ForegroundColor Yellow

function Check-Service {
    param([string]$ServiceName)
    
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        $status = docker-compose ps | Select-String $ServiceName
        if ($status -match "healthy|Up") {
            return $true
        }
        Start-Sleep -Seconds 2
        $attempt++
    }
    return $false
}

# Check each service
$services = @("db", "minio", "backend", "frontend")
foreach ($service in $services) {
    Write-Host "  Checking $service..." -NoNewline
    if (Check-Service -ServiceName $service) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [TIMEOUT]" -ForegroundColor Red
    }
}

# Initialize MinIO
Write-Host ""
Write-Host "[4/5] Initializing MinIO bucket..." -ForegroundColor Cyan
& ".\scripts\init-minio.ps1"

# Run migrations
Write-Host ""
Write-Host "[5/5] Running database migrations..." -ForegroundColor Cyan
try {
    docker-compose exec -T backend alembic upgrade head
} catch {
    Write-Host "  (Migrations may have already been applied)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Local environment is ready!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  Frontend:      http://localhost:3000"
Write-Host "  Backend API:   http://localhost:8001"
Write-Host "  API Docs:      http://localhost:8001/docs"
Write-Host "  Database:      localhost:5432"
Write-Host "  MinIO Console: http://localhost:9001"
Write-Host "    Username: minioadmin"
Write-Host "    Password: minioadmin"
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  View logs:  docker-compose logs -f [service]"
Write-Host "  Stop all:   .\scripts\stop-local.ps1"
Write-Host ""
