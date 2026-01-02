from fastapi import FastAPI
from app.router import router
from app.config import settings
from starlette.middleware.cors import CORSMiddleware
import app.model

import os
import logging
from contextlib import asynccontextmanager
from app.utils import set_snowflake_generator
from snowflake import SnowflakeGenerator

# Import rate limiter early to ensure it initializes
from app.middleware import rate_limiter

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- runs once per worker at startup ---
    worker_id = os.getpid() % 1024
    gen = SnowflakeGenerator(worker_id)
    set_snowflake_generator(gen)
    logger.info(
        f"Worker PID {os.getpid()} snowflake generator initialized with worker id {worker_id}"
    )
    yield
    # --- runs once per worker at shutdown ---
    # (clean-up code if needed)


def create_app():
    # Use environment variable for debug mode, default to False for production
    debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
    # Disable redirect_slashes to prevent HTTP redirects on HTTPS sites (causes mixed content errors)
    app = FastAPI(lifespan=lifespan, debug=debug_mode, redirect_slashes=False)

    # Add CORS **before** routers
    # In production, restrict to frontend host only
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", settings.FRONTEND_HOST).split(
        ","
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Type"],  # optional, for streaming
    )

    # Now include routers
    app.include_router(router)

    return app
