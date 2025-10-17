#!/bin/bash
# Development environment startup script

set -e

echo "🚀 Starting development environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f backend/.env.template ]; then
        cp backend/.env.template .env
        echo "✅ Created .env file with default values."
        echo ""
        echo "⚠️  IMPORTANT: Default credentials are used!"
        echo "   - Database: postgres/postgres"
        echo "   - You need to add your GEMINI_API_KEY to .env"
        echo "   - Change SECRET_KEY in production!"
        echo ""
        read -p "Continue with default values? (y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Please edit .env and run this script again."
            exit 1
        fi
    else
        echo "❌ .env.template not found!"
        exit 1
    fi
fi

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service health
echo "🏥 Checking service health..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "📝 Services:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend:  http://localhost:5000"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f"
echo "   - Stop: docker-compose -f docker-compose.yml -f docker-compose.dev.yml down"
echo "   - Restart: docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart"
echo ""
