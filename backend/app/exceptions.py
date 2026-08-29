"""Custom application exceptions and their FastAPI exception handlers."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base class for all custom application exceptions."""

    def __init__(self, message: str, code: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(f"{resource} not found", "NOT_FOUND", status.HTTP_404_NOT_FOUND)


class ConflictError(AppException):
    """Raised when an action conflicts with the current state of a resource."""

    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, "CONFLICT", status.HTTP_409_CONFLICT)


class UnauthorizedError(AppException):
    """Raised when a request lacks valid authentication or permissions."""

    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message, "UNAUTHORIZED", status.HTTP_401_UNAUTHORIZED)


class ValidationError(AppException):
    """Raised when input data fails business-level validation."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, "VALIDATION_ERROR", status.HTTP_422_UNPROCESSABLE_ENTITY)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle any AppException subclass and return a consistent JSON error body."""
    logger.warning("AppException handled: %s (%s) on %s", exc.message, exc.code, request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for any exception not otherwise handled."""
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the given FastAPI app instance."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
