# Zeabur Deployment Guide

This guide explains how to deploy the RAG Chat Application to Zeabur using the unified Dockerfile.

## Architecture

The deployment uses a **single Docker container** that runs:
- **Nginx** (port 80) - Serves Vue frontend and proxies API requests
- **FastAPI backend** (port 5000) - Handles API requests via Gunicorn
- **External PostgreSQL** - Database hosted on Zeabur or other managed service

## Prerequisites

1. **Zeabur Account**: Sign up at [zeabur.com](https://zeabur.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables**: Prepare your environment configuration

## Deployment Steps

### 1. Create a New Project on Zeabur

1. Log in to Zeabur dashboard
2. Click "Create Project"
3. Give your project a name (e.g., "rag-chat-app")

### 2. Add PostgreSQL Database

1. In your project, click "Add Service"
2. Select "Database" → "PostgreSQL"
3. Zeabur will provision a PostgreSQL instance
4. Note the connection details (you'll use these in environment variables)

### 3. Deploy the Application

1. Click "Add Service" → "Git"
2. Connect your GitHub repository
3. Select the repository containing this project
4. Zeabur will automatically detect the `Dockerfile` in the root directory
5. Click "Deploy"

### 4. Configure Environment Variables

In the Zeabur dashboard for your service, add the following environment variables:

#### Required Variables

```bash
# Database Configuration (from Zeabur PostgreSQL service)
DATABASE_URL=postgresql://username:password@host:port/database
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=5432

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
GEMINI_API_KEY=your-gemini-api-key-here

# Application Settings
ENVIRONMENT=production
DEBUG=False
API_V1_STR=/api/v1
PROJECT_NAME=RAG Chat Application
```

#### Optional Variables

```bash
# OpenAI (if using OpenAI provider)
OPENAI_API_KEY=your-openai-key

# Anthropic (if using Anthropic provider)
ANTHROPIC_API_KEY=your-anthropic-key

# LLM Configuration
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_GEMINI_MODEL=gemini-2.5-flash-lite
DEFAULT_OPENAI_MODEL=gpt-4-turbo-preview
DEFAULT_ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Email Configuration (for password reset, etc.)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# Gemini File Search Configuration
GEMINI_FILE_SEARCH_MODEL=gemini-2.5-flash-lite
GEMINI_STORE_SIZE_LIMIT_GB=20
GEMINI_MAX_FILE_SIZE_MB=100

# CORS (Zeabur will provide your domain)
FRONTEND_HOST=https://your-app.zeabur.app
```

### 5. Get Database Connection from Zeabur

Zeabur PostgreSQL service provides connection details:

1. Click on your PostgreSQL service
2. Go to "Connect" tab
3. Copy the connection string
4. Use it for `DATABASE_URL` environment variable

### 6. Domain Configuration

Zeabur automatically provides a domain like `your-app.zeabur.app`. You can:

1. Use the default Zeabur domain
2. Add a custom domain in the service settings

Make sure to update `FRONTEND_HOST` environment variable with your domain.

## Port Configuration

The Dockerfile exposes **port 80**. Zeabur will automatically:
- Map port 80 to HTTPS (443) with automatic SSL certificates
- Handle all SSL/TLS termination
- Provide a public URL

**You don't need to change any port settings** - Zeabur handles this automatically.

## Build Process

When you deploy, Zeabur will:

1. **Build Frontend** (Node.js 22 Alpine)
   - Install npm dependencies
   - Build Vue app (`npm run build`)
   - Generate static files in `dist/`

2. **Build Backend** (Python 3.13 Slim)
   - Install system dependencies (gcc, libpq-dev, nginx)
   - Install Python packages from `requirements.txt`
   - Copy application code

3. **Combine Services**
   - Copy frontend build to `/usr/share/nginx/html`
   - Configure Nginx to serve frontend and proxy API
   - Set up startup script for both services

4. **Run Migrations & Start**
   - Start Nginx (serves frontend on port 80)
   - Run Alembic migrations (`alembic upgrade head`)
   - Start Gunicorn (serves backend on port 5000)

## Monitoring

### Health Checks

The Dockerfile includes health checks:
- Frontend health: `http://localhost/health`
- Backend health: `http://localhost:5000/api/v1/health`

### Logs

View logs in Zeabur dashboard:
1. Go to your service
2. Click "Logs" tab
3. Monitor both Nginx and FastAPI logs

### Expected Log Output

```
Starting Nginx...
Running database migrations...
INFO  [alembic.runtime.migration] Running upgrade -> xxx
Starting FastAPI backend...
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Using worker: uvicorn.workers.UvicornWorker
```

## Troubleshooting

### Build Failures

**Issue**: Docker build fails during npm install
- **Solution**: Check `frontend/package.json` node version requirements
- The Dockerfile uses Node 22 Alpine - ensure compatibility

**Issue**: Python dependencies fail to install
- **Solution**: Check `backend/requirements.txt` for incompatible versions
- System packages (gcc, libpq-dev) are already included for psycopg2

### Runtime Errors

**Issue**: Database connection errors
- **Solution**: Verify `DATABASE_URL` environment variable
- Ensure PostgreSQL service is running in the same Zeabur project
- Check network connectivity between services

**Issue**: 502 Bad Gateway
- **Solution**: Backend might not be starting
- Check logs for Python errors
- Verify `GEMINI_API_KEY` is set
- Ensure database migrations completed successfully

**Issue**: Frontend loads but API calls fail
- **Solution**: Check Nginx proxy configuration
- Verify backend is listening on port 5000
- Check CORS settings (`FRONTEND_HOST` variable)

### Migration Issues

**Issue**: Alembic migration fails
- **Solution**: Check database connection string
- Ensure PostgreSQL user has CREATE TABLE permissions
- Manually run migrations: `alembic upgrade head`

## Environment-Specific Configuration

### Frontend API URL

The frontend automatically uses relative URLs (`/api/v1/...`) which Nginx proxies to the backend. No need to set `VITE_API_BASE_URL` for production.

### Database Migrations

Migrations run automatically on container startup via the startup script:
```bash
cd /app/backend
alembic upgrade head || echo "Migration failed or not needed"
```

If migrations fail, the container will still start but may have database schema issues.

## Scaling Considerations

### Single Container Limitations

The current setup runs both frontend and backend in one container:
- ✅ **Simple deployment**: One container, one service
- ✅ **Cost-effective**: Single Zeabur service
- ⚠️ **Limited scaling**: Can't scale frontend/backend independently
- ⚠️ **Resource sharing**: Nginx and Gunicorn share CPU/memory

### Future Multi-Service Setup

For high-traffic applications, consider splitting into separate services:
1. Frontend service (Nginx only)
2. Backend service (FastAPI only)
3. PostgreSQL service (already separate)

This would require Docker Compose or multiple Zeabur services.

## Security Notes

1. **Always use HTTPS**: Zeabur provides free SSL certificates
2. **Rotate SECRET_KEY**: Generate a strong, unique secret key
3. **Secure API keys**: Never commit API keys to Git
4. **Database credentials**: Use Zeabur's built-in secrets management
5. **CORS configuration**: Set `FRONTEND_HOST` to your actual domain

## Cost Optimization

- **Free Tier**: Zeabur offers free tier for small projects
- **Database**: PostgreSQL charges based on usage
- **Bandwidth**: Monitor API usage and file uploads
- **Storage**: Clean up old documents periodically

## Updates and Redeployment

To deploy updates:
1. Push changes to your GitHub repository
2. Zeabur automatically detects changes and rebuilds
3. Or manually trigger deployment in Zeabur dashboard

**Zero-downtime deployments**: Zeabur handles rolling updates automatically.

## Support

- **Zeabur Docs**: [docs.zeabur.com](https://docs.zeabur.com)
- **GitHub Issues**: Report issues in your repository
- **Project README**: See [README.md](README.md) for application details
