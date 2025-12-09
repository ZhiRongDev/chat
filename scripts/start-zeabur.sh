#!/bin/bash
set -e

# Start nginx in the background
echo "Starting Nginx..."
nginx -g "daemon off;" &

# Wait a bit for nginx to start
sleep 2

# Run database migrations
echo "Running database migrations..."
cd /app/backend
alembic upgrade head || echo "Migration failed or not needed"

# Start FastAPI backend with Gunicorn
echo "Starting FastAPI backend..."
exec gunicorn -c gunicorn.conf.py main:app
