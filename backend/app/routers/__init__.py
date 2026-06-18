from fastapi import FastAPI

from backend.app.routers import execution, health, interventions, workflow


def register_routers(app: FastAPI) -> None:
    app.include_router(health.router, prefix="/api")
    app.include_router(execution.router, prefix="/api")
    app.include_router(workflow.router, prefix="/api")
    app.include_router(interventions.router, prefix="/api")
