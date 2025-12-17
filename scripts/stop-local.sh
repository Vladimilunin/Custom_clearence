#!/bin/bash
# Stop local development environment

echo "🛑 Stopping local development environment..."

docker-compose down

echo "✅ All services stopped"
echo ""
echo "💡 To remove all data (including database and MinIO):"
echo "   docker-compose down -v"
echo ""
echo "🚀 To start again:"
echo "   ./scripts/start-local.sh"
