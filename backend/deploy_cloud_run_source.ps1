# Deploy backend to Google Cloud Run from source
# This uses Cloud Build to build and deploy directly

$ErrorActionPreference = "Stop"

Write-Host "[DEPLOY] Starting Cloud Run deployment from source..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Load environment variables from .env.cloud file
$envFile = ".env.cloud"
if (Test-Path $envFile) {
    Write-Host "[CONFIG] Loading production credentials from $envFile..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#].+?)=(.+)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
} else {
    Write-Host "[ERROR] $envFile file not found!" -ForegroundColor Red
    exit 1
}

# Configuration
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "tamozh-backend-479110" }
$SERVICE_NAME = "backend-service"
$REGION = "us-central1"

Write-Host "[INFO] Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "[INFO] Service: $SERVICE_NAME" -ForegroundColor Cyan
Write-Host "[INFO] Region: $REGION" -ForegroundColor Cyan
Write-Host ""

# Set project
gcloud config set project $PROJECT_ID

# Deploy from source using Cloud Build
Write-Host "[DEPLOY] Deploying from source..." -ForegroundColor Cyan
Write-Host "This will build the image using Cloud Build" -ForegroundColor Yellow
Write-Host ""

gcloud run deploy $SERVICE_NAME `
  --source . `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --timeout 300 `
  --memory 1Gi `
  --cpu 1 `
  --min-instances 0 `
  --max-instances 5 `
  --set-env-vars "DATABASE_URL=$env:DATABASE_URL,OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY,SILICONFLOW_API_KEY=$env:SILICONFLOW_API_KEY,S3_ENDPOINT=$env:S3_ENDPOINT,S3_ACCESS_KEY=$env:S3_ACCESS_KEY,S3_SECRET_KEY=$env:S3_SECRET_KEY,S3_BUCKET_NAME=$env:S3_BUCKET_NAME,S3_PUBLIC_DOMAIN=$env:S3_PUBLIC_DOMAIN"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    exit 1
}

# Get service URL
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "[SUCCESS] Deployment completed!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
Write-Host ""
Write-Host "[INFO] Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host "[INFO] API Docs: $SERVICE_URL/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "[TEST] Test the service:" -ForegroundColor Yellow
Write-Host "  curl $SERVICE_URL" -ForegroundColor White
