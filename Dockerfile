# ============================================
# Multi-stage Dockerfile for Zeabur Deployment
# Combines Frontend (Vue + Nginx) + Backend (FastAPI)
# ============================================

# ---- Frontend Build Stage ----
FROM node:22-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY ./frontend/package*.json ./
RUN npm ci

# Copy source code and build
COPY ./frontend ./
RUN npm run build

# ---- Backend Base Stage ----
FROM python:3.13-slim AS backend-base

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies for psycopg2 and other native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY ./backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# ---- Production Stage ----
FROM backend-base AS production

WORKDIR /app

# Copy backend application
COPY ./backend ./backend

# Copy frontend build from frontend-build stage
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Create nginx configuration that serves frontend and proxies API to backend
RUN echo 'server {\n\
    listen 8080;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    # Gzip compression\n\
    gzip on;\n\
    gzip_vary on;\n\
    gzip_min_length 1024;\n\
    gzip_proxied any;\n\
    gzip_comp_level 6;\n\
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;\n\
\n\
    # Proxy API requests to backend\n\
    location /api/ {\n\
        proxy_pass http://127.0.0.1:5000;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
        proxy_read_timeout 300s;\n\
        proxy_connect_timeout 75s;\n\
    }\n\
\n\
    # Cache static assets\n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
    }\n\
\n\
    # SPA fallback - serve index.html for all non-API requests\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
\n\
    # Security headers\n\
    add_header X-Frame-Options "SAMEORIGIN" always;\n\
    add_header X-Content-Type-Options "nosniff" always;\n\
    add_header X-XSS-Protection "1; mode=block" always;\n\
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;\n\
\n\
    # Health check endpoint\n\
    location /health {\n\
        access_log off;\n\
        return 200 "healthy\\n";\n\
        add_header Content-Type text/plain;\n\
    }\n\
}' > /etc/nginx/sites-available/default

# Remove default nginx config and update nginx.conf to use port 8080
RUN rm -f /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default && \
    sed -i 's/listen 80/listen 8080/g' /etc/nginx/nginx.conf || true

# Create startup script that runs both nginx and backend
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start nginx in the background\n\
echo "Starting Nginx..."\n\
nginx -g "daemon off;" &\n\
\n\
# Wait a bit for nginx to start\n\
sleep 2\n\
\n\
# Run database migrations\n\
echo "Running database migrations..."\n\
cd /app/backend\n\
alembic upgrade head || echo "Migration failed or not needed"\n\
\n\
# Start FastAPI backend with Gunicorn\n\
echo "Starting FastAPI backend..."\n\
exec gunicorn -c gunicorn.conf.py main:app\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port 8080 for HTTP (Zeabur requirement)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health && curl -f http://localhost:5000/api/v1/health || exit 1

# Set working directory to backend for the application
WORKDIR /app/backend

# Start both nginx and backend
CMD ["/app/start.sh"]
