# Docker Deployment Guide

This document provides comprehensive instructions for deploying the Chat Application using Docker.

## Table of Contents
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Development Environment](#development-environment)
- [Production Environment](#production-environment)
- [Scripts](#scripts)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (optional, for using Makefile commands)

### Development

```bash
# Quick start
make dev

# Or manually
./scripts/dev.sh

# Or with docker-compose directly
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Access:
- Frontend: http://localhost:5173 (with hot-reload)
- Backend: http://localhost:5000
- PostgreSQL: localhost:5432

### Production

```bash
# Quick start
make prod

# Or manually
./scripts/prod.sh

# With backup before deployment
./scripts/prod.sh --backup
```

Access:
- Frontend: http://localhost:80
- Backend: http://localhost:5000

## Architecture

### Multi-Stage Docker Builds

#### Backend (Python/FastAPI)
- **Base Stage**: Common dependencies and system packages
- **Dependencies Stage**: Python packages installation
- **Development Stage**: Includes dev tools (watchdog, debugpy) with hot-reload
- **Production Stage**: Optimized image with Gunicorn, non-root user

#### Frontend (Vue 3/Vite)
- **Base Stage**: Node.js setup
- **Dependencies Stage**: npm packages installation
- **Development Stage**: Vite dev server with hot-reload
- **Build Stage**: Production build
- **Production Stage**: Nginx serving static files

### Services

1. **Frontend**: Vue 3 SPA served via Nginx (prod) or Vite dev server (dev)
2. **Backend**: FastAPI application with Uvicorn (dev) or Gunicorn (prod)
3. **PostgreSQL**: Database with health checks

### Networks
All services communicate via the `app-network` bridge network.

## Development Environment

### Features
- ✅ Hot-reload enabled for both frontend and backend
- ✅ Source code mounted as volumes
- ✅ All ports exposed for direct access
- ✅ Debug tools included
- ✅ Development-specific database

### Commands

```bash
# Start development environment
make dev

# View logs
make logs ENV=dev
# Or for specific service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend

# Restart a service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart backend

# Execute commands in containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python -m pytest
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec frontend npm run test:unit

# Stop environment
make stop
```

### Hot-Reload

#### Backend (Python)
- Files are mounted at `/app/backend`
- Uvicorn's `--reload` flag watches for changes
- Changes to `.py` files automatically restart the server

#### Frontend (Vue/Vite)
- Files are mounted at `/app/frontend`
- Vite dev server watches for changes
- HMR (Hot Module Replacement) updates browser instantly
- Access via http://localhost:5173

### Environment Variables
Copy `backend/.env.template` to `.env` and configure:

```env
# Database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=chat_dev

# Application
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key

# URLs
FRONTEND_HOST=http://localhost:5173
```

## Production Environment

### Features
- ✅ Optimized, minimal Docker images
- ✅ Non-root users for security
- ✅ No volumes (code baked into images)
- ✅ Gunicorn with multiple workers
- ✅ Nginx with caching and compression
- ✅ Health checks for all services
- ✅ Resource limits and restart policies

### Deployment

```bash
# Initial deployment
make prod

# Update deployment
git pull
make prod

# With database backup
./scripts/prod.sh --backup
```

### Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **Non-root Users**: All containers run as non-root
3. **Network Isolation**: Internal services not exposed externally
4. **Image Security**: Using official Alpine-based images
5. **Secrets Management**: Use Docker secrets or external vault

### Scaling

Scale backend workers:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3
```

### Monitoring

```bash
# Health check all services
make health ENV=prod

# View resource usage
docker stats frontend backend postgres_db

# View logs
make logs ENV=prod
```

## Scripts

### Available Scripts

| Script | Description |
|--------|-------------|
| `scripts/dev.sh` | Start development environment |
| `scripts/prod.sh` | Deploy production environment |
| `scripts/logs.sh` | View logs for services |
| `scripts/health-check.sh` | Run health checks |
| `scripts/db-backup.sh` | Create database backup |
| `scripts/db-restore.sh` | Restore database from backup |

### Database Management

#### Backup
```bash
# Development database
make backup ENV=dev

# Production database
make backup ENV=prod
```

Backups are stored in `backups/` directory with timestamps.

#### Restore
```bash
# Restore production database
make restore FILE=backups/prod_db_backup_20250119_120000.sql.gz ENV=prod

# Restore development database
make restore FILE=backups/dev_db_backup_20250119_120000.sql.gz ENV=dev
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :5000
# Or
netstat -tuln | grep 5000

# Stop conflicting services
make stop
```

#### Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs backend

# Check container status
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Rebuild containers
make rebuild
```

#### Database Connection Issues
```bash
# Check database health
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db pg_isready

# Check environment variables
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend env | grep POSTGRES

# Restart database
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart db
```

#### Hot-Reload Not Working

**Backend:**
- Ensure volume is mounted: check `docker-compose.dev.yml`
- Check if uvicorn is running with `--reload` flag
- View logs: `docker-compose logs -f backend`

**Frontend:**
- Ensure volume is mounted correctly
- Check Vite config has `host: '0.0.0.0'`
- Try clearing browser cache
- View logs: `docker-compose logs -f frontend`

#### Permission Issues
```bash
# Reset permissions
sudo chown -R $USER:$USER .

# Or rebuild with correct permissions
make rebuild
```

### Clean Slate

If everything is broken:
```bash
# Nuclear option - removes everything
make clean

# Start fresh
make dev
```

## Best Practices

### Development
1. Always use `make dev` for local development
2. Keep `.env` file secure and never commit it
3. Use health checks before debugging: `make health ENV=dev`
4. Monitor logs regularly: `make logs ENV=dev`

### Production
1. Always backup before deployment: `./scripts/prod.sh --backup`
2. Test in staging environment first
3. Monitor resource usage after deployment
4. Set up automated backups (cron job)
5. Use Docker secrets for sensitive data

### Maintenance
1. Regular backups: Set up daily cron jobs
2. Update base images regularly for security patches
3. Monitor disk usage: Docker volumes can grow large
4. Clean up old images: `docker image prune -a`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Create .env file
        run: |
          echo "${{ secrets.ENV_FILE }}" > .env

      - name: Deploy
        run: |
          ./scripts/prod.sh --backup

      - name: Health Check
        run: |
          ./scripts/health-check.sh prod
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

## Support

For issues or questions:
1. Check logs: `make logs ENV=dev`
2. Run health check: `make health ENV=dev`
3. Review this documentation
4. Check project issues on GitHub
