# Deploy backend to Google Cloud Run using .env.cloud
# PowerShell version for cloud deployment

$ErrorActionPreference = "Stop"

Write-Host "[DEPLOY] Starting Cloud Run deployment..." -ForegroundColor Cyan
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
    Write-Host "Please create $envFile with your production credentials" -ForegroundColor Yellow
    Write-Host "You can use .env.cloud.example as a template" -ForegroundColor Yellow
    exit 1
}

# Configuration
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { gcloud config get-value project }
$SERVICE_NAME = "backend-service"
$REGION = "us-central1"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "[INFO] Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "[INFO] Region: $REGION" -ForegroundColor Cyan
Write-Host ""

# Check required environment variables
$required_vars = @(
    "DATABASE_URL",
    "OPENROUTER_API_KEY",
    "SILICONFLOW_API_KEY",
    "S3_ENDPOINT",
    "S3_ACCESS_KEY",
    "S3_SECRET_KEY",
    "S3_BUCKET_NAME"
)

$missing = @()
foreach ($var in $required_vars) {
    if (-not (Test-Path "env:$var")) {
        $missing += $var
    }
}

if ($missing.Count -gt 0) {
    Write-Host "[ERROR] Missing required environment variables:" -ForegroundColor Red
    foreach ($var in $missing) {
        Write-Host "  - $var" -ForegroundColor Red
    }
    exit 1
}

Write-Host "[OK] All required variables loaded" -ForegroundColor Green
Write-Host ""

# Check if gcloud CLI is installed
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "[ERROR] gcloud CLI is not installed" -ForegroundColor Red
    Write-Host "Please install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check authentication
Write-Host "[AUTH] Checking Google Cloud authentication..." -ForegroundColor Cyan
try {
    $account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if (-not $account) {
        Write-Host "[WARN] Not authenticated. Running gcloud auth login..." -ForegroundColor Yellow
        gcloud auth login
    } else {
        Write-Host "[OK] Authenticated as: $account" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Authentication check failed" -ForegroundColor Red
    exit 1
}

# Set project
Write-Host "[CONFIG] Setting project to $PROJECT_ID..." -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

# Build Docker image
Write-Host ""
Write-Host "[BUILD] Building Docker image..." -ForegroundColor Cyan
docker build -t $IMAGE_TAG .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker build failed" -ForegroundColor Red
    exit 1
}

# Push image to GCR
Write-Host ""
Write-Host "[PUSH] Pushing image to Google Container Registry..." -ForegroundColor Cyan
docker push $IMAGE_TAG
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker push failed" -ForegroundColor Red
    exit 1
}

# Deploy to Cloud Run
Write-Host ""
Write-Host "[DEPLOY] Deploying to Cloud Run..." -ForegroundColor Cyan
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
  --set-env-vars "S3_PUBLIC_DOMAIN=$env:S3_PUBLIC_DOMAIN"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Cloud Run deployment failed" -ForegroundColor Red
    exit 1
}

# Get service URL
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "[SUCCESS] Deployment completed!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
Write-Host "[INFO] Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host "[INFO] API Docs: $SERVICE_URL/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "[TEST] Test the service:" -ForegroundColor Yellow
Write-Host "  curl $SERVICE_URL" -ForegroundColor White
Write-Host ""
