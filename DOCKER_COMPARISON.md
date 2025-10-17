# Development vs Production Comparison

## Configuration Differences

| Feature | Development | Production |
|---------|-------------|------------|
| **Docker Target** | `development` | `production` |
| **Source Code** | Mounted as volume | Baked into image |
| **Hot-Reload** | ✅ Enabled | ❌ Disabled |
| **Port Exposure** | All ports exposed | Minimal exposure |
| **Image Size (Backend)** | ~450MB | ~380MB |
| **Image Size (Frontend)** | ~450MB | ~25MB |
| **Non-root User** | ❌ Root | ✅ Non-root |
| **Restart Policy** | `unless-stopped` | `always` |

## Frontend Differences

### Development
```yaml
Service: Vite Dev Server
Port: 5173
Hot-Reload: HMR enabled
Source: Mounted volume
Node Modules: Bind mount (not overwritten)
Environment: NODE_ENV=development
Command: npm run dev -- --host 0.0.0.0
Image Size: ~450MB
```

### Production
```yaml
Service: Nginx
Port: 80
Hot-Reload: N/A (static files)
Source: Compiled and baked in
Build: Pre-compiled assets
Environment: NODE_ENV=production
Command: nginx -g "daemon off;"
Image Size: ~25MB
Features:
  - Gzip compression
  - Static asset caching
  - Security headers
  - SPA routing
```

## Backend Differences

### Development
```yaml
Service: Uvicorn
Port: 5000
Hot-Reload: --reload flag enabled
Source: Mounted volume
Workers: 1 (auto-reload)
Environment:
  - ENVIRONMENT=development
  - DEBUG=True
Command: python main.py
Additional Tools:
  - watchdog (for file watching)
  - debugpy (for debugging)
Image Size: ~450MB
```

### Production
```yaml
Service: Gunicorn + Uvicorn Workers
Port: 5000
Hot-Reload: Disabled
Source: Baked into image
Workers: 4 (configurable)
User: Non-root (appuser)
Environment:
  - ENVIRONMENT=production
  - DEBUG=False
Command: gunicorn -c gunicorn.conf.py main:app
Optimizations:
  - Multiple workers
  - Graceful shutdown
  - Health checks
  - No dev dependencies
Image Size: ~380MB
```

## Database Differences

### Development
```yaml
Image: postgres:16-alpine
Port: 5432 (exposed)
Volume: pg_data_dev
Database Name: chat_dev
External Access: ✅ Yes
```

### Production
```yaml
Image: postgres:16-alpine
Port: Not exposed (internal only)
Volume: pg_data
Database Name: chat_prod
External Access: ❌ No (Docker network only)
```

## Redis Differences

### Development
```yaml
Image: redis:7-alpine
Port: 6379 (exposed)
Volume: redis_data_dev
Max Memory: 256MB
Persistence: AOF enabled
External Access: ✅ Yes
```

### Production
```yaml
Image: redis:7-alpine
Port: Not exposed (internal only)
Volume: redis_data
Max Memory: 512MB
Persistence: AOF with optimized fsync
External Access: ❌ No (Docker network only)
Config:
  - appendfsync everysec
  - tcp-backlog 511
  - timeout 300
```

## Docker Compose Commands

### Development
```bash
# Start
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Or using Makefile
make dev

# Stop
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Rebuild
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
```

### Production
```bash
# Start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or using Makefile
make prod

# Stop
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Rebuild
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

## Performance Comparison

### Startup Time
| Environment | Cold Start | Warm Start |
|-------------|-----------|------------|
| Development | ~35-40s | ~10-15s |
| Production | ~25-30s | ~5-10s |

### Build Time (First Build)
| Service | Development | Production |
|---------|-------------|------------|
| Backend | ~2-3 min | ~3-4 min |
| Frontend | ~3-4 min | ~4-5 min |

### Build Time (Cached)
| Service | Development | Production |
|---------|-------------|------------|
| Backend | ~30s | ~45s |
| Frontend | ~1 min | ~1.5 min |

### Memory Usage (Idle)
| Service | Development | Production |
|---------|-------------|------------|
| Frontend | ~120MB | ~15MB |
| Backend | ~180MB | ~150MB |
| PostgreSQL | ~35MB | ~35MB |
| Redis | ~10MB | ~10MB |
| **Total** | ~345MB | ~210MB |

### Memory Usage (Active)
| Service | Development | Production |
|---------|-------------|------------|
| Frontend | ~150MB | ~20MB |
| Backend | ~250MB | ~600MB (4 workers) |
| PostgreSQL | ~80MB | ~80MB |
| Redis | ~25MB | ~50MB |
| **Total** | ~505MB | ~750MB |

## Security Comparison

| Feature | Development | Production |
|---------|-------------|------------|
| Non-root User | ❌ | ✅ |
| Network Isolation | Partial | Full |
| Port Exposure | All | Minimal |
| Debug Mode | ✅ Enabled | ❌ Disabled |
| Source Code Visibility | ✅ Mounted | ❌ Baked-in |
| SSL/TLS | Manual | Recommended |
| Secrets Management | .env file | Docker secrets |
| Security Headers | ❌ | ✅ |

## Volume Mounts

### Development
```yaml
Frontend:
  - ./frontend:/app/frontend
  - /app/frontend/node_modules (anonymous)

Backend:
  - ./backend:/app/backend
  - /app/backend/.venv (anonymous)
  - /app/backend/__pycache__ (anonymous)
```

### Production
```yaml
Frontend: None (static files baked into image)
Backend: None (code baked into image)
```

## Use Cases

### When to Use Development
- ✅ Local development
- ✅ Debugging
- ✅ Testing new features
- ✅ Hot-reload needed
- ✅ Frequent code changes
- ✅ Learning/experimentation

### When to Use Production
- ✅ Staging environment
- ✅ Production deployment
- ✅ Performance testing
- ✅ Security testing
- ✅ Load testing
- ✅ CI/CD pipelines

## Migration Path

### Development → Production

1. **Test in development**
   ```bash
   make dev
   # Test your changes
   ```

2. **Commit changes**
   ```bash
   git add .
   git commit -m "Your changes"
   ```

3. **Deploy to production**
   ```bash
   make prod
   ```

4. **Verify health**
   ```bash
   make health ENV=prod
   ```

### Production → Development (Debugging)

1. **Backup production data**
   ```bash
   make backup ENV=prod
   ```

2. **Stop production**
   ```bash
   make stop
   ```

3. **Start development**
   ```bash
   make dev
   ```

4. **Restore data (optional)**
   ```bash
   make restore FILE=backups/prod_backup.sql.gz ENV=dev
   ```

## Best Practices

### Development
- Keep source code outside container
- Use hot-reload for fast iteration
- Expose all ports for debugging
- Use development database
- Enable debug logging

### Production
- Bake code into image
- Use multiple workers
- Minimize port exposure
- Use production database
- Enable access logging
- Implement health checks
- Use non-root users
- Regular backups

## Quick Reference

| Task | Command |
|------|---------|
| Start dev | `make dev` |
| Start prod | `make prod` |
| View dev logs | `make logs ENV=dev` |
| View prod logs | `make logs ENV=prod` |
| Check dev health | `make health ENV=dev` |
| Check prod health | `make health ENV=prod` |
| Backup dev DB | `make backup ENV=dev` |
| Backup prod DB | `make backup ENV=prod` |
| Stop all | `make stop` |
| Clean all | `make clean` |
