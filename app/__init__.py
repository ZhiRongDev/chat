from fastapi import FastAPI
from app.router import router
from app.config import settings
from starlette.middleware.cors import CORSMiddleware
import app.model

import os
from contextlib import asynccontextmanager
from app.utils import set_snowflake_generator
from snowflake import SnowflakeGenerator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- runs once per worker at startup ---
    worker_id = os.getpid() % 1024
    gen = SnowflakeGenerator(worker_id)
    set_snowflake_generator(gen)
    print(
        f"Worker PID {os.getpid()} snowflake generator initialized with worker id {worker_id}"
    )
    yield
    # --- runs once per worker at shutdown ---
    # (clean-up code if needed)


def create_app():
    app = FastAPI(lifespan=lifespan, debug=True)
    app.include_router(router, prefix=settings.API_STR)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
