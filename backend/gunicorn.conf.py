import os
from snowflake import SnowflakeGenerator
from app.config import settings
from app.utils import set_snowflake_generator

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", 4))
worker_class = "uvicorn.workers.UvicornWorker"
bind = f"{settings.HOST}:{settings.PORT}"

# Only reload in development
reload = os.getenv("ENVIRONMENT", "production") == "development"

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"


def post_fork(server, worker):
    """Initialize Snowflake ID generator for each worker"""
    worker_id = worker.pid % 1024
    gen = SnowflakeGenerator(worker_id)
    set_snowflake_generator(gen)
    print(
        f"Worker PID {worker.pid} snowflake generator initialized with worker id {worker_id}"
    )
