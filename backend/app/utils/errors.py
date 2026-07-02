from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.schemas.errors import ErrorDetail, ErrorResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def error_payload(code: str, message: str, field: str | None = None) -> dict[str, object]:
    return ErrorResponse(error=ErrorDetail(code=code, message=message, field=field)).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        first_error = exc.errors()[0] if exc.errors() else {}
        location = ".".join(str(part) for part in first_error.get("loc", [])) or None
        return JSONResponse(
            status_code=422,
            content=error_payload(
                "request_validation_error",
                first_error.get("msg", "Request validation failed"),
                location,
            ),
        )
