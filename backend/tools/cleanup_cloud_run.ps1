# Cleanup Cloud Run Revisions and GCR Images
# Keeps the latest $KEEP_COUNT revisions/images

$KEEP_COUNT = 1
$SERVICE_NAME = "backend-service"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/tamozh-backend-479110/backend-service"

Write-Host "🚀 Starting Cloud Resource Cleanup..." -ForegroundColor Cyan
Write-Host "   Keeping latest $KEEP_COUNT versions." -ForegroundColor Gray

# 1. Clean Cloud Run Revisions
Write-Host "`n🔹 Cleaning Cloud Run Revisions..." -ForegroundColor Cyan

# Get all revisions sorted by creation time (newest first)
$revisions = gcloud run revisions list --service $SERVICE_NAME --region $REGION --format='value(name)' --sort-by="~createTime"

if ($revisions) {
    $revisionsArray = $revisions -split "`r`n"
    $count = $revisionsArray.Count
    Write-Host "   Found $count revisions."

    if ($count -gt $KEEP_COUNT) {
        $toDelete = $revisionsArray[$KEEP_COUNT..($count-1)]
        Write-Host "   Deleting $($toDelete.Count) old revisions..." -ForegroundColor Yellow
        
        foreach ($rev in $toDelete) {
            if ($rev) {
                Write-Host "   - Deleting $rev..."
                gcloud run revisions delete $rev --region $REGION --quiet
            }
        }
        Write-Host "   ✅ Revisions cleaned." -ForegroundColor Green
    } else {
        Write-Host "   ✨ Nothing to delete ($count -le $KEEP_COUNT)." -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️ No revisions found or error listing revisions." -ForegroundColor Red
}

# 2. Clean Container Registry (GCR)
Write-Host "`n🔹 Cleaning Container Registry (GCR)..." -ForegroundColor Cyan

# Get all image digests sorted by timestamp (newest first)
# Note: We list tags to get digests, but we delete by digest to remove the underlying storage
$images = gcloud container images list-tags $IMAGE_NAME --format='get(digest)' --sort-by="~timestamp"

if ($images) {
    $imagesArray = $images -split "`r`n"
    $count = $imagesArray.Count
    Write-Host "   Found $count images."

    if ($count -gt $KEEP_COUNT) {
        $toDelete = $imagesArray[$KEEP_COUNT..($count-1)]
        Write-Host "   Deleting $($toDelete.Count) old images..." -ForegroundColor Yellow
        
        foreach ($digest in $toDelete) {
            if ($digest) {
                $fullImage = "${IMAGE_NAME}@${digest}"
                Write-Host "   - Deleting $digest..."
                gcloud container images delete $fullImage --force-delete-tags --quiet
            }
        }
        Write-Host "   ✅ Images cleaned." -ForegroundColor Green
    } else {
        Write-Host "   ✨ Nothing to delete ($count -le $KEEP_COUNT)." -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️ No images found or error listing images." -ForegroundColor Red
}

Write-Host "`n🎉 Cloud Cleanup Complete!" -ForegroundColor Green
