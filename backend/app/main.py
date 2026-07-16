import sys
from pathlib import Path

# Add the project root to sys.path to allow absolute imports of 'backend'
# This is necessary because some deployment platforms (e.g. Render) may not preserve PYTHONPATH
root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.routers import register_routers
from backend.app.utils.errors import register_exception_handlers

LOCAL_CORS_ORIGINS = {
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
}


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Cipla EMEU Execution Intelligence API",
        version="0.1.0",
        debug=settings.app_env == "local",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(settings.cors_origin_list, settings.app_env),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    register_routers(app)

    return app


def _cors_origins(configured_origins: list[str], app_env: str) -> list[str]:
    origins = set(configured_origins)
    if app_env == "local":
        origins.update(LOCAL_CORS_ORIGINS)
    return sorted(origins)


app = create_app()
