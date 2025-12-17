#!/bin/bash
# Initialize MinIO bucket for local development

echo "🔧 Initializing MinIO..."

# Wait for MinIO to be ready
echo "⏳ Waiting for MinIO to be available..."
until curl -sf http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    sleep 2
done
echo "✅ MinIO is ready!"

# Install mc (MinIO Client) if not present
if ! command -v mc &> /dev/null; then
    echo "📦 Installing MinIO Client..."
    wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /tmp/mc
    chmod +x /tmp/mc
    MC_CMD="/tmp/mc"
else
    MC_CMD="mc"
fi

# Configure mc alias
echo "🔗 Configuring MinIO client..."
$MC_CMD alias set local http://localhost:9000 minioadmin minioadmin

# Create bucket if it doesn't exist
echo "📦 Creating bucket 'tamozh-images'..."
$MC_CMD mb local/tamozh-images --ignore-existing

# Set public read policy
echo "🔓 Setting public read policy..."
$MC_CMD anonymous set download local/tamozh-images

echo "✅ MinIO initialized successfully!"
echo ""
echo "📊 MinIO Console: http://localhost:9001"
echo "   Username: minioadmin"
echo "   Password: minioadmin"
echo ""
echo "🪣 Bucket: tamozh-images"
echo "   Endpoint: http://localhost:9000"
