from fastapi import FastAPI

from backend.app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Cipla EMEU Execution Intelligence API",
        version="0.1.0",
        debug=settings.app_env == "local",
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
