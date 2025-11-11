# ---- Base Stage ----
FROM python:3.13-slim AS base

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app/backend

# Install build dependencies for psycopg2 and other native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Dependencies Stage ----
FROM base AS dependencies

# Copy requirements first for caching
COPY ./backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---- Development Stage ----
FROM dependencies AS development

# Install development tools
RUN pip install --no-cache-dir \
    watchdog[watchmedo] \
    debugpy

# Copy all backend files
COPY ./backend ./

# Expose the same port FastAPI runs on
EXPOSE 5000

# Enable hot-reload with uvicorn
CMD ["python", "main.py"]

# ---- Production Stage ----
FROM dependencies AS production

# Copy all backend files
COPY ./backend ./

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the same port FastAPI runs on
EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
