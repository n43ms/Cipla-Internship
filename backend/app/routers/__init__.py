from fastapi import FastAPI

from backend.app.routers import health


def register_routers(app: FastAPI) -> None:
    app.include_router(health.router, prefix="/api")
