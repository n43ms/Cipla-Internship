from fastapi import FastAPI

from backend.app.config import get_settings
from backend.app.routers import register_routers
from backend.app.utils.errors import register_exception_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Cipla EMEU Execution Intelligence API",
        version="0.1.0",
        debug=settings.app_env == "local",
    )

    register_exception_handlers(app)
    register_routers(app)

    return app


app = create_app()
