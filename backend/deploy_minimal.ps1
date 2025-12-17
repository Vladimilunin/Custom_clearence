$PROJECT_ID="tamozh-backend-479110"
$IMAGE_TAG="gcr.io/$PROJECT_ID/backend-minimal"

# 1. Build the container
& "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" builds submit --tag $IMAGE_TAG --project $PROJECT_ID --quiet

# 2. Deploy the container
& "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" run deploy backend-minimal `
  --image $IMAGE_TAG `
  --platform managed `
  --region us-central1 `
  --project $PROJECT_ID `
  --quiet `
  --allow-unauthenticated `
  --port 8080
