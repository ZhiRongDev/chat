#!/bin/bash
# Health check script for all services

set -e

# Determine which environment
ENV=${1:-dev}

if [ "$ENV" == "prod" ]; then
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
    FRONTEND_URL="http://localhost:80"
    BACKEND_URL="http://localhost:5000"
else
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
    FRONTEND_URL="http://localhost:5173"
    BACKEND_URL="http://localhost:5000"
fi

echo "🏥 Running health checks for $ENV environment..."
echo ""

# Check Docker containers
echo "📦 Container Status:"
docker-compose $COMPOSE_FILES ps
echo ""

# Check backend health
echo "🔧 Backend Health:"
if curl -sf "$BACKEND_URL/api/v1/health" > /dev/null 2>&1; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend is unhealthy or not responding"
fi
echo ""

# Check frontend
echo "🎨 Frontend Health:"
if curl -sf "$FRONTEND_URL" > /dev/null 2>&1; then
    echo "   ✅ Frontend is accessible"
else
    echo "   ❌ Frontend is not accessible"
fi
echo ""

# Check database
echo "🗄️  Database Health:"
if docker-compose $COMPOSE_FILES exec -T db pg_isready > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is ready"
else
    echo "   ❌ PostgreSQL is not ready"
fi
echo ""

# Check Redis
echo "📦 Redis Health:"
if docker-compose $COMPOSE_FILES exec -T redis redis-cli ping | grep -q PONG; then
    echo "   ✅ Redis is responding"
else
    echo "   ❌ Redis is not responding"
fi
echo ""

# Resource usage
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    frontend backend postgres_db redis 2>/dev/null || echo "   (Container stats unavailable)"
echo ""

echo "✅ Health check complete!"
