"""Exception handler for centralized error management.

Provides custom exceptions, logging, and HTTP response formatting
for production-ready error handling.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from functools import wraps
import json

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = 500,
                 error_code: str = "INTERNAL_ERROR", 
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for JSON response."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "status_code": self.status_code,
                "timestamp": self.timestamp,
                "details": self.details
            }
        }


class ValidationError(APIException):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class AuthenticationError(APIException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401, "AUTHENTICATION_ERROR")


class AuthorizationError(APIException):
    """Raised when user lacks permissions."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403, "AUTHORIZATION_ERROR")


class RateLimitError(APIException):
    """Raised when rate limit exceeded."""

    def __init__(self, remaining_seconds: int):
        details = {"retry_after": remaining_seconds}
        super().__init__(
            "Rate limit exceeded",
            429,
            "RATE_LIMIT_EXCEEDED",
            details
        )
        self.retry_after = remaining_seconds


class NotFoundError(APIException):
    """Raised when resource not found."""

    def __init__(self, resource: str, resource_id: Any):
        message = f"{resource} with id {resource_id} not found"
        details = {"resource": resource, "resource_id": str(resource_id)}
        super().__init__(message, 404, "NOT_FOUND", details)


class ExternalServiceError(APIException):
    """Raised when external service fails."""

    def __init__(self, service: str, reason: str):
        message = f"{service} service error: {reason}"
        details = {"service": service, "reason": reason}
        super().__init__(message, 502, "SERVICE_UNAVAILABLE", details)


class ExceptionHandler:
    """Centralized exception handling utility."""

    @staticmethod
    def log_exception(exc: Exception, context: Optional[Dict] = None) -> None:
        """Log exception with context."""
        context = context or {}
        logger.error(
            f"Exception occurred: {exc.__class__.__name__}",
            exc_info=True,
            extra={"context": context}
        )

    @staticmethod
    def handle_exception(exc: Exception, request_id: Optional[str] = None
                        ) -> Dict[str, Any]:
        """Handle exception and return API response."""
        ExceptionHandler.log_exception(exc, {"request_id": request_id})

        if isinstance(exc, APIException):
            return exc.to_dict()

        # Handle unknown exceptions
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        }

    @staticmethod
    def handle_exceptions(func: Callable) -> Callable:
        """Decorator for automatic exception handling."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except APIException as e:
                logger.error(f"API Exception: {e.message}",
                           extra={"error_code": e.error_code})
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}",
                           exc_info=True)
                raise APIException(
                    "Internal server error",
                    500,
                    "INTERNAL_ERROR"
                )
        return wrapper


def format_error_response(error_dict: Dict[str, Any],
                        status_code: Optional[int] = None
                        ) -> tuple:
    """Format error response for HTTP."""
    if status_code is None:
        status_code = error_dict.get("error", {}).get("status_code", 500)
    return error_dict, status_code
