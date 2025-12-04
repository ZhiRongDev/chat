# Setup Guide

This guide will help you set up the RAG Chat Application for development or production.

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Node.js ^20.19.0 or >=22.12.0 + Python 3.13+ for local development
- Git

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone <repository-url>
cd chat
```

### 2. Create Environment Configuration

Copy the template and configure your environment:

```bash
cp .env.template .env
```

Edit `.env` and update the following **required** variables:

```bash
# REQUIRED: Change these values
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
DB_PASSWORD=your-secure-database-password
POSTGRES_PASSWORD=your-secure-database-password  # Must match DB_PASSWORD

# OPTIONAL: Add your LLM API keys (or provide via UI later)
# GEMINI_API_KEY=your-gemini-api-key
# OPENAI_API_KEY=your-openai-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 3. Start the Application

**Development mode** (with hot-reload):
```bash
make dev
# Or: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Production mode**:
```bash
make prod
# Or: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Access the Application

- **Development**:
  - Frontend: http://localhost:5173
  - Backend API: http://localhost:5000
  - Database: localhost:5432

- **Production**:
  - Frontend: http://localhost
  - Backend API: http://localhost:5000 (or via frontend proxy)

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key for authentication | Generate with `openssl rand -hex 32` |
| `DB_PASSWORD` | PostgreSQL database password | `your-secure-password` |
| `POSTGRES_PASSWORD` | Must match DB_PASSWORD | `your-secure-password` |

### Database Configuration

| Variable | Development | Production | Description |
|----------|------------|------------|-------------|
| `DB_HOST` | `db` | `db` | Use `db` for Docker, `localhost` for local |
| `DB_USER` | `postgres` | `postgres` | Database user |
| `DB_NAME` | `chat_dev` | `chat_prod` | Database name |
| `DB_PORT` | `5432` | `5432` | Database port |

### Redis Configuration

| Variable | Development | Production | Description |
|----------|------------|------------|-------------|
| `REDIS_HOST` | `redis` | `redis` | Use `redis` for Docker, `localhost` for local |
| `REDIS_PORT` | `6379` | `6379` | Redis port |
| `REDIS_DB` | `0` | `0` | Redis database number |

### CORS Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `FRONTEND_HOST` | Primary frontend URL for CORS and email verification links | `http://localhost:5173` (dev) or `http://localhost` (prod) |
| `ALLOWED_ORIGINS` | Additional allowed origins (comma-separated) | `http://localhost:5173,http://localhost,http://localhost:80` |

**Important for Production**:
1. Set `ALLOWED_ORIGINS` to include both dev and production origins:
   ```bash
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost,http://localhost:80
   ```

2. `FRONTEND_HOST` is automatically overridden to `http://localhost` in production via `docker-compose.prod.yml`
   - This ensures email verification and password reset links point to the correct URL
   - Development uses: `http://localhost:5173`
   - Production uses: `http://localhost` (set in docker-compose.prod.yml)

### LLM API Keys (Optional)

| Variable | Description | Get API Key |
|----------|-------------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `OPENAI_API_KEY` | OpenAI API key | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | [Anthropic Console](https://console.anthropic.com/) |

> **Note**: API keys can be provided via the frontend UI if not set in `.env`

### Search API Keys (Optional)

| Variable | Description | Get API Key |
|----------|-------------|-------------|
| `SERPER_API_KEY` | Google Search via Serper | [Serper.dev](https://serper.dev) |
| `TAVILY_API_KEY` | Tavily Search | [Tavily.com](https://tavily.com) |

### Email Configuration (Optional)

| Variable | Description | Required For |
|----------|-------------|--------------|
| `FROM_EMAIL` | Email address for sending notifications | Password reset functionality |

> **Note**: Requires Gmail API credentials setup (see Email Setup section)

## Makefile Commands

The project includes a Makefile for easy management:

```bash
make help         # Show all available commands
make dev          # Start development environment
make prod         # Deploy production environment
make start        # Start services without rebuilding
make stop         # Stop all services
make logs ENV=dev # View logs (ENV=dev or prod)
make health       # Run health checks
make backup       # Create database backup
make restore      # Restore database from backup
make clean        # Remove all containers and volumes
make rebuild      # Rebuild all images from scratch
```

## Security Best Practices

### 1. Generate a Strong Secret Key

```bash
# Generate a secure random secret key
openssl rand -hex 32
```

Add this to your `.env`:
```bash
SECRET_KEY=<generated-key>
```

### 2. Use Strong Database Passwords

Don't use the default `postgres` password in production:
```bash
DB_PASSWORD=your-very-secure-random-password-here
POSTGRES_PASSWORD=your-very-secure-random-password-here
```

### 3. Never Commit `.env` File

The `.env` file is already in `.gitignore`. Verify:
```bash
git check-ignore .env  # Should return: .env
```

### 4. Restrict CORS Origins in Production

Only allow trusted origins:
```bash
# Development: Allow dev server
ALLOWED_ORIGINS=http://localhost:5173

# Production: Only allow your domain
ALLOWED_ORIGINS=https://yourdomain.com
```

### 5. Review Docker User Configuration

Production containers run as non-root users for security:
- Backend: runs as `appuser` (UID 1000)
- Frontend: runs as `nginx` (UID 101)

## Troubleshooting

### CORS Errors

If you see CORS errors like "No 'Access-Control-Allow-Origin' header":

1. Check `ALLOWED_ORIGINS` in `.env`:
   ```bash
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost
   ```

2. Restart the backend:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart backend
   ```

### Database Connection Issues

1. Ensure database is running:
   ```bash
   docker-compose ps
   ```

2. Check database logs:
   ```bash
   docker-compose logs db
   ```

3. Verify `DB_HOST` is set correctly:
   - Docker: `DB_HOST=db`
   - Local: `DB_HOST=localhost`

### Port Conflicts

If ports are already in use:

1. Check what's using the port:
   ```bash
   lsof -i :5000  # Backend
   lsof -i :5173  # Frontend dev
   lsof -i :5432  # PostgreSQL
   ```

2. Stop conflicting services or change ports in `.env`

## Local Development (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (requires PostgreSQL installed)
# Update .env: DB_HOST=localhost, REDIS_HOST=localhost

# Run migrations
alembic upgrade head

# Start server
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## Production Deployment

### Using Docker Compose

```bash
# Deploy with automatic backup
make prod --backup

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Database Backups

```bash
# Create backup
make backup

# Restore from backup
make restore FILE=backups/backup_20231201_120000.sql.gz
```

### Monitoring

```bash
# View logs
make logs ENV=prod

# Check health
make health

# Check container status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

## Additional Resources

- [CLAUDE.md](CLAUDE.md) - Project documentation for AI assistants
- [Frontend README](frontend/README.md) - Frontend development guide
- [Backend README](backend/README.md) - Backend API documentation

## Support

For issues and questions:
- Check the [troubleshooting section](#troubleshooting)
- Review logs: `make logs ENV=dev` or `make logs ENV=prod`
- Open an issue on GitHub
