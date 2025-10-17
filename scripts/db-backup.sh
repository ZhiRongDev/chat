#!/bin/bash
# Database backup script

set -e

# Determine which environment
ENV=${1:-prod}

if [ "$ENV" == "prod" ]; then
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
    POSTGRES_DB=${POSTGRES_DB:-chat_prod}
else
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
    POSTGRES_DB=${POSTGRES_DB:-chat_dev}
fi

# Create backups directory
mkdir -p backups

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/${ENV}_db_backup_${TIMESTAMP}.sql"

echo "💾 Creating database backup for $ENV environment..."
echo "   Database: $POSTGRES_DB"
echo "   File: $BACKUP_FILE"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create backup
docker-compose $COMPOSE_FILES exec -T db \
    pg_dump -U "${POSTGRES_USER:-postgres}" "$POSTGRES_DB" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "✅ Backup created successfully!"
echo "   File: ${BACKUP_FILE}.gz"
echo "   Size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"
echo ""

# Keep only last 7 backups
echo "🧹 Cleaning up old backups (keeping last 7)..."
ls -t backups/${ENV}_db_backup_*.sql.gz | tail -n +8 | xargs -r rm
echo "✅ Cleanup complete!"
