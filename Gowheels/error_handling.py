"""
Centralized error handling for GoWheels
Provides standardized error responses without information leakage
"""

import logging
import traceback
from typing import Optional, Dict, Any
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('gowheels.errors')


class ErrorCode:
    """Standardized error codes"""
    # Client errors (4xx)
    BAD_REQUEST = 'BAD_REQUEST'
    UNAUTHORIZED = 'UNAUTHORIZED'
    FORBIDDEN = 'FORBIDDEN'
    NOT_FOUND = 'NOT_FOUND'
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'
    
    # Server errors (5xx)
    INTERNAL_ERROR = 'INTERNAL_ERROR'
    SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE'
    DATABASE_ERROR = 'DATABASE_ERROR'


class APIError(Exception):
    """Base exception for API errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )


class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401
        )


class AuthorizationError(APIError):
    """Authorization error"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403
        )


class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404
        )


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429
        )


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    correlation_id: Optional[str] = None,
    details: Optional[Dict] = None
) -> JsonResponse:
    """
    Create standardized error response
    
    Args:
        error_code: Error code constant
        message: User-friendly error message
        status_code: HTTP status code
        correlation_id: Request correlation ID
        details: Additional error details (only in DEBUG mode)
    
    Returns:
        JsonResponse with standardized error format
    """
    error_response = {
        'success': False,
        'error': {
            'code': error_code,
            'message': message,
        }
    }
    
    # Add correlation ID if available
    if correlation_id:
        error_response['error']['correlation_id'] = correlation_id
    
    # Only include details in DEBUG mode
    if settings.DEBUG and details:
        error_response['error']['details'] = details
    
    return JsonResponse(error_response, status=status_code)


def handle_exception(
    exception: Exception,
    request=None,
    include_traceback: bool = False
) -> JsonResponse:
    """
    Handle exception and return appropriate error response
    
    Args:
        exception: The exception to handle
        request: Django request object (optional)
        include_traceback: Include traceback in response (DEBUG only)
    
    Returns:
        JsonResponse with error details
    """
    correlation_id = getattr(request, 'correlation_id', None) if request else None
    
    # Handle custom API errors
    if isinstance(exception, APIError):
        logger.warning(
            f"API Error: {exception.error_code} - {exception.message}",
            extra={
                'correlation_id': correlation_id,
                'error_code': exception.error_code,
                'status_code': exception.status_code,
            }
        )
        
        return create_error_response(
            error_code=exception.error_code,
            message=exception.message,
            status_code=exception.status_code,
            correlation_id=correlation_id,
            details=exception.details if settings.DEBUG else None
        )
    
    # Log unexpected errors with full details
    logger.error(
        f"Unhandled exception: {type(exception).__name__}: {str(exception)}",
        extra={
            'correlation_id': correlation_id,
            'exception_type': type(exception).__name__,
        },
        exc_info=True
    )
    
    # Generic error response (no sensitive info)
    error_message = "An internal error occurred. Please try again later."
    
    # In DEBUG mode, include exception details
    details = None
    if settings.DEBUG:
        details = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
        }
        if include_traceback:
            details['traceback'] = traceback.format_exc()
    
    return create_error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        message=error_message,
        status_code=500,
        correlation_id=correlation_id,
        details=details
    )


def sanitize_error_message(message: str) -> str:
    """
    Sanitize error message to prevent information leakage
    
    Args:
        message: Original error message
    
    Returns:
        Sanitized error message
    """
    # Remove file paths
    import re
    message = re.sub(r'[A-Za-z]:\\[^\s]+', '[PATH]', message)
    message = re.sub(r'/[^\s]+\.py', '[FILE]', message)
    
    # Remove SQL queries
    if 'SELECT' in message.upper() or 'INSERT' in message.upper():
        return "Database operation failed"
    
    # Remove stack traces
    if 'Traceback' in message:
        return "An internal error occurred"
    
    return message


# Common error responses
def bad_request(message: str = "Invalid request", correlation_id: str = None) -> JsonResponse:
    """Return 400 Bad Request"""
    return create_error_response(
        ErrorCode.BAD_REQUEST,
        message,
        400,
        correlation_id
    )


def unauthorized(message: str = "Authentication required", correlation_id: str = None) -> JsonResponse:
    """Return 401 Unauthorized"""
    return create_error_response(
        ErrorCode.UNAUTHORIZED,
        message,
        401,
        correlation_id
    )


def forbidden(message: str = "Permission denied", correlation_id: str = None) -> JsonResponse:
    """Return 403 Forbidden"""
    return create_error_response(
        ErrorCode.FORBIDDEN,
        message,
        403,
        correlation_id
    )


def not_found(message: str = "Resource not found", correlation_id: str = None) -> JsonResponse:
    """Return 404 Not Found"""
    return create_error_response(
        ErrorCode.NOT_FOUND,
        message,
        404,
        correlation_id
    )


def internal_error(message: str = "Internal server error", correlation_id: str = None) -> JsonResponse:
    """Return 500 Internal Server Error"""
    return create_error_response(
        ErrorCode.INTERNAL_ERROR,
        message,
        500,
        correlation_id
    )


def service_unavailable(message: str = "Service temporarily unavailable", correlation_id: str = None) -> JsonResponse:
    """Return 503 Service Unavailable"""
    return create_error_response(
        ErrorCode.SERVICE_UNAVAILABLE,
        message,
        503,
        correlation_id
    )
