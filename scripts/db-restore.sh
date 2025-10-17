#!/bin/bash
# Database restore script

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <backup_file.sql.gz> [environment]"
    echo ""
    echo "Available backups:"
    ls -lh backups/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1
ENV=${2:-prod}

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

if [ "$ENV" == "prod" ]; then
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
    POSTGRES_DB=${POSTGRES_DB:-chat_prod}
else
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
    POSTGRES_DB=${POSTGRES_DB:-chat_dev}
fi

echo "⚠️  WARNING: This will overwrite the current $ENV database!"
echo "   Database: $POSTGRES_DB"
echo "   Backup: $BACKUP_FILE"
echo ""
read -p "Are you sure? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "💾 Restoring database from backup..."

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "📦 Decompressing backup..."
    gunzip -c "$BACKUP_FILE" | docker-compose $COMPOSE_FILES exec -T db \
        psql -U "${POSTGRES_USER:-postgres}" "$POSTGRES_DB"
else
    cat "$BACKUP_FILE" | docker-compose $COMPOSE_FILES exec -T db \
        psql -U "${POSTGRES_USER:-postgres}" "$POSTGRES_DB"
fi

echo "✅ Database restored successfully!"
