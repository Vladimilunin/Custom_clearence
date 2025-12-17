"""
Custom exceptions for the TamozhGen application.
Provides structured error handling across the application.
"""


class TamozhGenError(Exception):
    """Base exception for all TamozhGen errors."""
    pass


class ParsingError(TamozhGenError):
    """Error during PDF parsing."""
    
    def __init__(self, message: str, page: int | None = None, details: dict | None = None):
        self.page = page
        self.details = details or {}
        super().__init__(message)


class APIKeyExhaustedError(ParsingError):
    """All API keys have been exhausted."""
    
    def __init__(self, page: int, attempted_keys: int, attempted_models: int):
        self.attempted_keys = attempted_keys
        self.attempted_models = attempted_models
        super().__init__(
            f"Page {page} failed after trying {attempted_keys} keys and {attempted_models} models",
            page=page,
            details={"attempted_keys": attempted_keys, "attempted_models": attempted_models}
        )


class PDFRenderError(ParsingError):
    """Error rendering PDF to images."""
    
    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message, details={"original_error": str(original_error) if original_error else None})


class ImageProcessingError(TamozhGenError):
    """Error processing images."""
    
    def __init__(self, image_path: str, message: str):
        self.image_path = image_path
        super().__init__(f"Error processing image '{image_path}': {message}")


class ValidationError(TamozhGenError):
    """Validation error for input data."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for '{field}': {message}")


class FileValidationError(ValidationError):
    """File validation error."""
    
    def __init__(self, filename: str, message: str):
        super().__init__(field="file", message=f"'{filename}': {message}")
        self.filename = filename


class PathTraversalError(ValidationError):
    """Path traversal attack detected."""
    
    def __init__(self, path: str):
        super().__init__(field="path", message=f"Path traversal detected: {path}")
        self.path = path


class DocumentGenerationError(TamozhGenError):
    """Error generating DOCX documents."""
    
    def __init__(self, document_type: str, message: str):
        self.document_type = document_type
        super().__init__(f"Error generating {document_type}: {message}")


class DatabaseError(TamozhGenError):
    """Database operation error."""
    pass


class ExternalServiceError(TamozhGenError):
    """Error from external service (Groq, S3, etc.)."""
    
    def __init__(self, service: str, message: str, status_code: int | None = None):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} error: {message}")
