"""Exception handlers and custom exceptions."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AkoweException(Exception):
    """Base exception for AkoweAI."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class TransactionProcessingError(AkoweException):
    """Raised when transaction processing fails."""

    def __init__(self, detail: str = "Failed to process transaction"):
        super().__init__(400, detail)


class WhatsAppIntegrationError(AkoweException):
    """Raised when WhatsApp integration fails."""

    def __init__(self, detail: str = "WhatsApp integration error"):
        super().__init__(503, detail)


class DatabaseError(AkoweException):
    """Raised when database operation fails."""

    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(500, detail)


class AuthenticationError(AkoweException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(401, detail)


class AuthorizationError(AkoweException):
    """Raised when user is not authorized."""

    def __init__(self, detail: str = "User not authorized"):
        super().__init__(403, detail)


class ResourceNotFoundError(AkoweException):
    """Raised when resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(404, detail)


class ValidationError(AkoweException):
    """Raised when validation fails."""

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(422, detail)


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers."""

    @app.exception_handler(AkoweException)
    async def akowe_exception_handler(request: Request, exc: AkoweException):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        logger.error(
            f"AkoweException: {exc.detail}",
            extra={
                "path": str(request.url),
                "status_code": exc.status_code,
                "request_id": request_id
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        logger.exception(
            f"Unhandled exception: {str(exc)}",
            extra={
                "path": str(request.url),
                "request_id": request_id
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add request ID to all requests."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
