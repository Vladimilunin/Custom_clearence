#!/bin/bash
# Start local development environment with all services

set -e

echo "🚀 Starting Local Development Environment..."
echo "=============================================="
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Start all services
echo "🐳 Starting Docker Compose services..."
docker-compose up -d --build

# Wait for all services to be healthy
echo "⏳ Waiting for services to be ready..."
echo "   This may take a minute..."

# Function to check service health
check_service() {
    local service=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep "$service" | grep -q "healthy\|Up"; then
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    return 1
}

# Check each service
services=("db" "minio" "backend" "frontend")
for service in "${services[@]}"; do
    echo -n "   Checking $service..."
    if check_service "$service"; then
        echo " ✅"
    else
        echo " ❌ (timeout)"
    fi
done

# Initialize MinIO
echo ""
echo "🪣 Initializing MinIO bucket..."
./scripts/init-minio.sh

# Run migrations
echo ""
echo "📊 Running database migrations..."
docker-compose exec -T backend alembic upgrade head || echo "⚠️  Migrations may have already been applied"

echo ""
echo "=============================================="
echo "✅ Local environment is ready!"
echo "=============================================="
echo ""
echo "📱 Services:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8001"
echo "   API Docs:     http://localhost:8001/docs"
echo "   Database:     localhost:5432"
echo "   MinIO Console: http://localhost:9001"
echo "      Username: minioadmin"
echo "      Password: minioadmin"
echo ""
echo "📝 Logs: docker-compose logs -f [service]"
echo "🛑 Stop: ./scripts/stop-local.sh"
echo ""
