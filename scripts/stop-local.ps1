# Stop local development environment
# PowerShell version

Write-Host "Stopping local development environment..." -ForegroundColor Yellow

docker-compose down

Write-Host "[OK] All services stopped" -ForegroundColor Green
Write-Host ""
Write-Host "To remove all data (including database and MinIO):" -ForegroundColor Cyan
Write-Host "  docker-compose down -v"
Write-Host ""
Write-Host "To start again:" -ForegroundColor Cyan
Write-Host "  .\scripts\start-local.ps1"
