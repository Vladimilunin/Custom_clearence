# Deploy backend using Google Cloud Build (no local Docker required)
# PowerShell version

$ErrorActionPreference = "Stop"

Write-Host "[DEPLOY] Starting Cloud Build deployment..." -ForegroundColor Cyan
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
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { gcloud config get-value project }
$SERVICE_NAME = "backend-service"
$REGION = "us-central1"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "[INFO] Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "[INFO] Region: $REGION" -ForegroundColor Cyan

# Check gcloud
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "[ERROR] gcloud CLI is not installed" -ForegroundColor Red
    exit 1
}

# 1. Submit Build to Cloud Build
Write-Host ""
Write-Host "[BUILD] Submitting build to Cloud Build..." -ForegroundColor Cyan
Write-Host "(This runs in the cloud, no local Docker required)" -ForegroundColor Gray

# Submit the build using cloudbuild.yaml
# We rely on the cloudbuild.yaml in the current directory
gcloud builds submit --config cloudbuild.yaml .

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Cloud Build failed" -ForegroundColor Red
    exit 1
}

# 2. Deploy to Cloud Run (using the image just built)
Write-Host ""
Write-Host "[DEPLOY] Deploying to Cloud Run..." -ForegroundColor Cyan

# We use the same deploy command as before, but pointing to the image we just built/pushed
gcloud run deploy $SERVICE_NAME `
  --image $IMAGE_TAG `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --timeout 300 `
  --memory 1Gi `
  --cpu 1 `
  --min-instances 0 `
  --max-instances 5 `
  --concurrency 80 `
  --set-env-vars "DATABASE_URL=$env:DATABASE_URL" `
  --set-env-vars "OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY" `
  --set-env-vars "SILICONFLOW_API_KEY=$env:SILICONFLOW_API_KEY" `
  --set-env-vars "S3_ENDPOINT=$env:S3_ENDPOINT" `
  --set-env-vars "S3_ACCESS_KEY=$env:S3_ACCESS_KEY" `
  --set-env-vars "S3_SECRET_KEY=$env:S3_SECRET_KEY" `
  --set-env-vars "S3_BUCKET_NAME=$env:S3_BUCKET_NAME" `
  --set-env-vars "S3_PUBLIC_DOMAIN=$env:S3_PUBLIC_DOMAIN" `
  --set-env-vars "GROQ_API_KEYS=$env:GROQ_API_KEYS"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Cloud Run deployment failed" -ForegroundColor Red
    exit 1
}

# Get service URL
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "[SUCCESS] Deployment completed via Cloud Build!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
Write-Host "[INFO] Service URL: $SERVICE_URL" -ForegroundColor Cyan
