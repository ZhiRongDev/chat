from fastapi import FastAPI
from app.router import router
from app.config import settings


def create_app():
    app = FastAPI(debug=True)
    app.include_router(router, prefix=settings.API_V1_STR)

    return app
