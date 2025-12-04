#!/bin/bash
# Production deployment script

set -e

echo "🚀 Starting production deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Create a .env file with production configuration."
    exit 1
fi

# Validate environment variables
required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env; then
        echo "❌ Required environment variable ${var} not found in .env"
        exit 1
    fi
done

# Pull latest changes (if in a git repo and tracking branch exists)
if [ -d .git ]; then
    echo "📥 Pulling latest changes..."
    git pull 2>/dev/null || echo "⚠️  Skipping git pull (no tracking branch or failed)"
fi

# Backup database (if needed)
if [ "$1" == "--backup" ]; then
    echo "💾 Creating database backup..."
    mkdir -p backups
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db \
        pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "backups/db_backup_${timestamp}.sql"
    echo "✅ Database backed up to backups/db_backup_${timestamp}.sql"
fi

# Build and deploy
echo "🔨 Building images..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

echo "🔄 Stopping old containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

echo "🚀 Starting new containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo ""
echo "✅ Production deployment complete!"
echo ""
echo "📝 Services:"
echo "   - Frontend: http://localhost:80"
echo "   - Backend:  http://localhost:5000 (or via frontend proxy)"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f"
echo "   - Stop: docker-compose -f docker-compose.yml -f docker-compose.prod.yml down"
echo "   - Restart: docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart"
echo ""
