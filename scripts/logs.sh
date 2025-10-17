#!/bin/bash
# View logs for services

set -e

# Determine which environment
ENV=${1:-dev}

if [ "$ENV" == "prod" ]; then
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
else
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
fi

# Get specific service or all services
SERVICE=${2:-}

echo "📋 Viewing logs for $ENV environment..."
echo ""

if [ -z "$SERVICE" ]; then
    docker-compose $COMPOSE_FILES logs -f --tail=100
else
    docker-compose $COMPOSE_FILES logs -f --tail=100 "$SERVICE"
fi
