# ---- Backend ----
FROM python:3.13-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app/backend

# Install build dependencies for psycopg2 and other native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY ./backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY ./backend ./

# Copy environment file (optional — docker-compose can inject it too)
COPY .env /app/backend/.env

# Expose the same port Flask runs on
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]
