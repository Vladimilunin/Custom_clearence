"""
Application-specific exceptions for better error handling.

Usage:
    from app.exceptions import NotFoundError, ValidationError
    
    raise NotFoundError("Part", part_id)
    raise ValidationError("Invalid file format")
"""
from typing import Any, Optional


class AppError(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        result = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result


class NotFoundError(AppError):
    """Resource not found."""
    
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, "NOT_FOUND")


class ValidationError(AppError):
    """Input validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(message, "VALIDATION_ERROR", details)


class ExternalServiceError(AppError):
    """External service (S3, AI API) error."""
    
    def __init__(self, service: str, message: str, original_error: Optional[Exception] = None):
        details = {"service": service}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(f"{service}: {message}", "EXTERNAL_SERVICE_ERROR", details)


class RateLimitError(AppError):
    """Rate limit exceeded."""
    
    def __init__(self, service: str, retry_after: Optional[int] = None):
        details = {"service": service}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(f"Rate limit exceeded for {service}", "RATE_LIMIT", details)


class AIParsingError(AppError):
    """AI parsing failed."""
    
    def __init__(self, model: str, message: str, attempts: int = 0):
        details = {"model": model, "attempts": attempts}
        super().__init__(f"AI parsing failed: {message}", "AI_PARSING_ERROR", details)
