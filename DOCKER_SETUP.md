# Docker Setup Guide

This guide explains how to run the Gemini File Search RAG application using Docker.

## Quick Start

### 1. Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Make (optional, for convenience commands)

### 2. Initial Setup

```bash
# 1. Clone the repository
cd /path/to/chat

# 2. Copy environment template
cp backend/.env.template .env

# 3. Edit .env and set required variables
nano .env
# At minimum, set:
#   GEMINI_API_KEY=your-gemini-api-key-here
#   SECRET_KEY=your-secret-key-here

# 4. Start services in development mode
make dev
# OR manually:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## What's Changed (Gemini File Search Migration)

### Backend Changes

**Removed Dependencies:**

- ❌ FAISS CPU (`faiss-cpu`)
- ❌ ChromaDB (`chromadb`)
- ❌ Tiktoken (`tiktoken`)
- ❌ Sentence Transformers (`sentence-transformers`)
- ❌ Langchain Chroma (`langchain-chroma`)

**Simplified Configuration:**

- ❌ Removed: `CUDA_VISIBLE_DEVICES`, `TORCH_DEVICE` (no longer needed)
- ❌ Removed: Vector store volume mounts
- ✅ Added: Gemini File Search service

**Docker Changes:**

1. [docker/backend/Dockerfile](docker/backend/Dockerfile) - Removed PyTorch/CUDA environment variables
2. [docker-compose.dev.yml](docker-compose.dev.yml) - Removed vector store volume mounts
3. Backend now ~40% lighter and faster to build

### Frontend Changes

**API Updates:**

1. RAG mode now requires authentication (`Authorization: Bearer <token>`)
2. Removed parameters: `top_k`, `min_score`
3. Added parameter: `max_output_tokens` (512-8192)
4. Document responses include `gemini_file_id` field

**UI Updates:**

1. [ChatSettings.vue](frontend/src/components/ChatSettings.vue) - Updated for Gemini File Search
2. RAG indicator shows "Gemini File Search RAG Active"
3. Settings panel shows info about automatic optimization

## Development Workflow

### Starting Services

```bash
# Development mode with hot-reload
make dev

# OR start without rebuilding
make start

# View logs
make logs

# View specific service logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f frontend
```

### Stopping Services

```bash
# Stop all services
make stop

# OR manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

### Database Management

```bash
# Run migrations
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head

# Create new migration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic revision -m "migration message"

# Access PostgreSQL shell
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db psql -U postgres -d chat_dev

# Backup database
make backup

# Restore database
make restore FILE=backups/backup_file.sql.gz
```

### Testing

```bash
# Backend tests
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend pytest

# Frontend E2E tests
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec frontend npm run test:e2e

# Test Gemini File Search integration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python test_gemini_file_search.py
```

### Debugging

```bash
# View service status
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Check health
make health

# Access backend shell
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend /bin/bash

# Access frontend shell
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec frontend /bin/sh

# View container logs
docker logs backend -f
docker logs frontend -f
```

## Production Deployment

### 1. Environment Setup

```bash
# Copy production env template
cp backend/.env.template .env.prod

# Edit production environment
nano .env.prod

# Required production variables:
# - GEMINI_API_KEY
# - SECRET_KEY (generate strong random key)
# - DB_PASSWORD (strong password)
# - POSTGRES_PASSWORD (same as DB_PASSWORD)
```

### 2. Deploy

```bash
# Start production services
make prod

# OR manually
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

### 3. Production Configuration

Production mode uses:

- **Nginx** for frontend (port 80)
- **Gunicorn** for backend (port 5000)
- Optimized builds
- Non-root users for security
- Persistent volumes for data

## Architecture

### Services

```
┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │
│  (Vite/Vue) │     │  (FastAPI)  │
│  Port: 5173 │     │  Port: 5000 │
└─────────────┘     └─────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐      ┌──────▼──────┐
         │  PostgreSQL │      │    Redis    │
         │  Port: 5432 │      │  Port: 6379 │
         └─────────────┘      └─────────────┘
                │
                │
         ┌──────▼──────────────┐
         │  Gemini File Search │
         │  (Google Cloud)     │
         └─────────────────────┘
```

### Volumes

- `pg_data_dev` - PostgreSQL data (development)
- `redis_data_dev` - Redis data (development)
- `pg_data` - PostgreSQL data (production)
- `redis_data` - Redis data (production)

**Note**: Vector store volumes have been removed as Gemini File Search handles all storage.

### Networks

- `app-network` - Bridge network connecting all services

## Environment Variables

### Required

```bash
# Backend
GEMINI_API_KEY=your-gemini-api-key-here  # REQUIRED for RAG
SECRET_KEY=your-secret-key-here          # JWT secret
DB_PASSWORD=your-db-password
POSTGRES_PASSWORD=your-db-password        # Same as DB_PASSWORD

# Frontend (set in docker-compose.dev.yml)
VITE_API_BASE_URL=http://localhost:5000
```

### Optional

```bash
# LLM Providers (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Search APIs (optional)
SERPER_API_KEY=your-serper-key
TAVILY_API_KEY=your-tavily-key

# Gemini File Search Settings
GEMINI_FILE_SEARCH_MODEL=gemini-2.5-flash-lite
GEMINI_STORE_SIZE_LIMIT_GB=20
GEMINI_MAX_FILE_SIZE_MB=100

# Database
DB_HOST=db                               # 'db' for Docker, 'localhost' for local
DB_USER=postgres
DB_NAME=chat_dev
DB_PORT=5432

# Redis
REDIS_HOST=redis                         # 'redis' for Docker, 'localhost' for local
REDIS_PORT=6379
REDIS_DB=0
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs backend

# Common issues:
# 1. GEMINI_API_KEY not set
#    Solution: Set in .env file
#
# 2. Database connection error
#    Solution: Ensure DB_HOST=db in .env for Docker
#
# 3. Port already in use
#    Solution: Change PORT in .env or stop conflicting service
```

### Frontend won't build

```bash
# Check logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs frontend

# Common issues:
# 1. Node version mismatch
#    Solution: Rebuild with --no-cache
#
# 2. VITE_API_BASE_URL incorrect
#    Solution: Check docker-compose.dev.yml environment
```

### Database migration errors

```bash
# Reset migrations (CAUTION: deletes data)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
```

### RAG not working

```bash
# 1. Check if GEMINI_API_KEY is set
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend printenv | grep GEMINI

# 2. Verify user is authenticated
#    RAG requires login - check localStorage for 'token'

# 3. Check if documents are uploaded
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/v1/documents/

# 4. Test Gemini File Search service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python test_gemini_file_search.py
```

### Build cache issues

```bash
# Rebuild without cache
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache

# OR use make
make rebuild
```

## Performance Tips

### Development

1. **Hot Reload**: Changes to source code automatically reload
2. **Volume Mounts**: Code changes reflect immediately without rebuilding
3. **Separate Volumes**: Development uses separate DB/Redis volumes

### Production

1. **Build Optimization**: Multi-stage builds reduce image size
2. **Gunicorn Workers**: Configured in `gunicorn.conf.py`
3. **Nginx**: Serves frontend with caching headers
4. **Non-root Users**: Security best practice

## Migration from Old RAG System

### If upgrading from FAISS/ChromaDB:

1. **Backup existing data**:

   ```bash
   make backup
   ```

2. **Run migration**:

   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
   ```

3. **Re-upload documents**:

   - Old vector store data is not compatible
   - Users must re-upload documents via the UI or API

4. **Update environment**:
   - Remove old RAG settings from `.env`
   - Add Gemini File Search settings

## Useful Commands Reference

```bash
# Start/Stop
make dev                 # Start development
make start               # Start without rebuild
make stop                # Stop services
make rebuild             # Rebuild images

# Logs
make logs                # All services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f frontend

# Database
make backup              # Backup database
make restore FILE=...    # Restore database

# Health
make health              # Check all services
curl http://localhost:5000/api/v1/health

# Clean
make stop                # Stop services
make clean               # Remove all (with confirmation)
docker system prune -a   # Clean Docker system
```

## Support

For issues or questions:

1. Check [QUICKSTART_GEMINI_FILE_SEARCH.md](QUICKSTART_GEMINI_FILE_SEARCH.md)
2. Review [GEMINI_FILE_SEARCH_MIGRATION.md](backend/GEMINI_FILE_SEARCH_MIGRATION.md)
3. Consult [CLAUDE.md](CLAUDE.md)
4. Open an issue in the repository

---

**Ready to go!** Start with `make dev` and visit http://localhost:5173
