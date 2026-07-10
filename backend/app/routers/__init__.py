from fastapi import FastAPI

from backend.app.routers import (
    ai,
    budget,
    data_quality,
    doctors,
    execution,
    health,
    ingestion,
    interventions,
    workflow,
)


def register_routers(app: FastAPI) -> None:
    app.include_router(health.router, prefix="/api")
    app.include_router(execution.router, prefix="/api")
    app.include_router(workflow.router, prefix="/api")
    app.include_router(interventions.router, prefix="/api")
    app.include_router(budget.router, prefix="/api")
    app.include_router(doctors.router, prefix="/api")
    app.include_router(data_quality.router, prefix="/api")
    app.include_router(ingestion.router, prefix="/api")
    app.include_router(ai.router, prefix="/api")
