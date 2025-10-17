# Quick Start Guide

## Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

## Setup (First Time)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd chat

# 2. Create environment file
cp backend/.env.template .env

# 3. Edit .env with your configuration
nano .env  # or use your preferred editor
```

Required variables in `.env`:
```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=chat_dev
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
FRONTEND_HOST=http://localhost:5173
```

## Development

```bash
# Start development environment (with hot-reload)
make dev

# Access services
# Frontend: http://localhost:5173
# Backend:  http://localhost:5000
# Database: localhost:5432
# Redis:    localhost:6379

# View logs
make logs ENV=dev

# Stop services
make stop
```

## Production

```bash
# Deploy production
make prod

# Access services
# Frontend: http://localhost:80
# Backend:  http://localhost:5000

# View logs
make logs ENV=prod

# Create backup
make backup ENV=prod
```

## Common Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start development with hot-reload |
| `make prod` | Deploy production |
| `make logs ENV=dev` | View logs (dev/prod) |
| `make health ENV=dev` | Check services health |
| `make backup ENV=prod` | Backup database |
| `make stop` | Stop all services |
| `make clean` | Remove everything |

## Development Workflow

1. **Start services**: `make dev`
2. **Make changes**: Edit code in `frontend/` or `backend/`
3. **Auto-reload**: Changes apply automatically
4. **View logs**: `make logs ENV=dev` (if needed)
5. **Stop**: `make stop` or `Ctrl+C`

## Production Deployment

1. **Update code**: `git pull`
2. **Backup**: `make backup ENV=prod`
3. **Deploy**: `make prod`
4. **Verify**: `make health ENV=prod`

## Hot-Reload Features

### Backend (Python/FastAPI)
- ✅ Code changes auto-reload
- ✅ No rebuild needed
- ✅ Instant feedback

### Frontend (Vue 3/Vite)
- ✅ Hot Module Replacement (HMR)
- ✅ Instant browser updates
- ✅ State preservation

## Troubleshooting

### Services won't start
```bash
make stop
make dev
```

### Port already in use
```bash
# Find and kill process using port
lsof -i :5173  # frontend
lsof -i :5000  # backend
```

### Database connection error
```bash
# Check database status
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db pg_isready

# View database logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs db
```

### Hot-reload not working
```bash
# Restart service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart backend
# or
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart frontend
```

### Nuclear option (clean slate)
```bash
make clean  # Removes everything
make dev    # Start fresh
```

## File Structure

```
chat/
├── docker-compose.yml          # Base configuration
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.prod.yml     # Production overrides
├── Makefile                    # Quick commands
├── .env                        # Environment variables (create this)
│
├── docker/
│   ├── backend/
│   │   ├── Dockerfile         # Backend multi-stage build
│   └── frontend/
│       ├── Dockerfile         # Frontend multi-stage build
│       └── nginx.conf         # Production nginx config
│
├── scripts/
│   ├── dev.sh                 # Development startup
│   ├── prod.sh                # Production deployment
│   ├── logs.sh                # View logs
│   ├── health-check.sh        # Health checks
│   ├── db-backup.sh           # Database backup
│   └── db-restore.sh          # Database restore
│
├── backend/                   # Python/FastAPI code
└── frontend/                  # Vue 3 code
```

## Next Steps

- Read [DOCKER_README.md](DOCKER_README.md) for detailed documentation
- Read [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) for implementation details
- Configure CI/CD in [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml)

## Support

For issues:
1. Check logs: `make logs ENV=dev`
2. Run health check: `make health ENV=dev`
3. Review [DOCKER_README.md](DOCKER_README.md)
4. Check GitHub issues
