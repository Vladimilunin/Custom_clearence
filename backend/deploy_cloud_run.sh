#!/bin/bash
# Deploy backend to Google Cloud Run using .env.cloud

set -e

echo "🚀 Deploying Backend to Cloud Run..."
echo "===================================================="

# Load environment variables from .env.cloud file
ENV_FILE=".env.cloud"
if [ -f "$ENV_FILE" ]; then
    echo "📝 Loading production credentials from $ENV_FILE..."
    export $(cat $ENV_FILE | grep -v '^#' | xargs)
else
    echo "❌ $ENV_FILE file not found!"
    echo "Please create $ENV_FILE with your production credentials"
    echo "You can use .env.cloud.example as a template"
    exit 1
fi

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
SERVICE_NAME="backend-service"
REGION="us-central1"

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check required environment variables
required_vars=("DATABASE_URL" "S3_ENDPOINT" "S3_ACCESS_KEY" "S3_SECRET_KEY" "S3_BUCKET_NAME")
missing=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing+=("$var")
    fi
done

if [ ${#missing[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing[@]}"; do
        echo "   - $var"
    done
    echo "Please add them to $ENV_FILE"
    exit 1
fi

echo "✅ All required environment variables present"
echo ""

# 1. Build the container image
echo "🔨 Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""

# 2. Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 300 \
  --concurrency 80 \
  --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
  --set-env-vars "OPENROUTER_API_KEY=${OPENROUTER_API_KEY}" \
  --set-env-vars "SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}" \
  --set-env-vars "S3_ENDPOINT=${S3_ENDPOINT}" \
  --set-env-vars "S3_ACCESS_KEY=${S3_ACCESS_KEY}" \
  --set-env-vars "S3_SECRET_KEY=${S3_SECRET_KEY}" \
  --set-env-vars "S3_BUCKET_NAME=${S3_BUCKET_NAME}" \
  --set-env-vars "S3_PUBLIC_DOMAIN=${S3_PUBLIC_DOMAIN}"

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed!"
    exit 1
fi

echo ""
echo "===================================================="
echo "✅ Deployment complete!"
echo "===================================================="
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)")
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "   1. Test the API: $SERVICE_URL/docs"
echo "   2. Update frontend NEXT_PUBLIC_API_URL to: $SERVICE_URL"
echo "   3. Deploy frontend with: ../scripts/deploy-frontend-vercel.sh"
