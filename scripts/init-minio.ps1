# Initialize MinIO bucket for local development
# PowerShell version

Write-Host "[MinIO] Initializing..." -ForegroundColor Cyan

# Wait for MinIO to be ready
Write-Host "[MinIO] Waiting for service to be available..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
do {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) { break }
    } catch {}
    Start-Sleep -Seconds 2
    $attempt++
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Host "[ERROR] MinIO did not become ready in time" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] MinIO is ready!" -ForegroundColor Green

# Check if mc.exe exists
$mcPath = "C:\tools\mc.exe"
if (-not (Test-Path $mcPath)) {
    Write-Host "[MinIO] Downloading MinIO Client..." -ForegroundColor Yellow
    $mcUrl = "https://dl.min.io/client/mc/release/windows-amd64/mc.exe"
    New-Item -ItemType Directory -Force -Path "C:\tools" | Out-Null
    Invoke-WebRequest -Uri $mcUrl -OutFile $mcPath
}

# Configure mc alias
Write-Host "[MinIO] Configuring MinIO client..." -ForegroundColor Cyan
& $mcPath alias set local http://localhost:9000 minioadmin minioadmin 2>&1 | Out-Null

# Create bucket if it doesn't exist
Write-Host "[MinIO] Creating bucket 'tamozh-images'..." -ForegroundColor Cyan
& $mcPath mb local/tamozh-images --ignore-existing 2>&1 | Out-Null

# Set public read policy
Write-Host "[MinIO] Setting public read policy..." -ForegroundColor Cyan
& $mcPath anonymous set download local/tamozh-images 2>&1 | Out-Null

Write-Host ""
Write-Host "[OK] MinIO initialized successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "MinIO Console: http://localhost:9001" -ForegroundColor Cyan
Write-Host "  Username: minioadmin"
Write-Host "  Password: minioadmin"
Write-Host ""
Write-Host "Bucket: tamozh-images" -ForegroundColor Cyan
Write-Host "  Endpoint: http://localhost:9000"
