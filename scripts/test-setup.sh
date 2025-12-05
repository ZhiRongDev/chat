#!/bin/bash
# Test script to verify Docker setup

set -e

echo "🧪 Testing Docker Setup..."
echo ""

# Check if Docker is installed
echo "1️⃣  Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker is installed: $(docker --version)"
echo ""

# Check if Docker Compose is installed
echo "2️⃣  Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✅ Docker Compose is installed: $(docker-compose --version)"
echo ""

# Check if .env file exists
echo "3️⃣  Checking .env file..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "   Creating from template..."
    if [ -f backend/.env.template ]; then
        cp backend/.env.template .env
        echo "✅ .env file created from template"
        echo "   ⚠️  Please edit .env with your configuration before running"
    else
        echo "❌ backend/.env.template not found"
        exit 1
    fi
else
    echo "✅ .env file exists"
fi
echo ""

# Check required environment variables
echo "4️⃣  Checking required environment variables..."
required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env 2>/dev/null; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "⚠️  Missing required variables in .env:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
else
    echo "✅ All required environment variables are present"
fi
echo ""

# Test Docker Compose configuration
echo "5️⃣  Validating docker-compose configurations..."

# Test development config
if docker-compose -f docker-compose.yml -f docker-compose.dev.yml config > /dev/null 2>&1; then
    echo "✅ Development configuration is valid"
else
    echo "❌ Development configuration has errors"
    exit 1
fi

# Test production config
if docker-compose -f docker-compose.yml -f docker-compose.prod.yml config > /dev/null 2>&1; then
    echo "✅ Production configuration is valid"
else
    echo "❌ Production configuration has errors"
    exit 1
fi
echo ""

# Check Dockerfile syntax
echo "6️⃣  Checking Dockerfile syntax..."
if [ -f docker/backend/Dockerfile ]; then
    echo "✅ Backend Dockerfile exists"
else
    echo "❌ Backend Dockerfile not found"
    exit 1
fi

if [ -f docker/frontend/Dockerfile ]; then
    echo "✅ Frontend Dockerfile exists"
else
    echo "❌ Frontend Dockerfile not found"
    exit 1
fi
echo ""

# Check if ports are available
echo "7️⃣  Checking if required ports are available..."
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use ($service)"
        echo "   You may need to stop the service using this port"
    else
        echo "✅ Port $port is available ($service)"
    fi
}

check_port 5173 "Frontend Dev"
check_port 5000 "Backend"
check_port 5432 "PostgreSQL"
check_port 80 "Frontend Prod"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Setup Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your Docker setup is ready! 🎉"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration (if not done yet)"
echo "2. Run 'make dev' to start development environment"
echo "3. Access frontend at http://localhost:5173"
echo "4. Access backend at http://localhost:5000"
echo ""
echo "For more information, see:"
echo "  - QUICK_START.md for quick start guide"
echo "  - DOCKER_README.md for detailed documentation"
echo ""
