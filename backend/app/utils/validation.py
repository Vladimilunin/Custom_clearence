"""
Validation utilities for file handling and security.
"""
import os
import re
from typing import BinaryIO
import logging

from app.exceptions import FileValidationError, PathTraversalError

logger = logging.getLogger(__name__)

# PDF magic bytes (file signature)
PDF_MAGIC_BYTES = b'%PDF'

# Maximum file size (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed file extensions
ALLOWED_PDF_EXTENSIONS = {'.pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


def validate_pdf_file(file_content: bytes, filename: str) -> None:
    """
    Validate that the uploaded file is a valid PDF.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Raises:
        FileValidationError: If validation fails
    """
    # Check file extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_PDF_EXTENSIONS:
        raise FileValidationError(filename, f"Invalid extension '{ext}'. Only PDF files are allowed.")
    
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        size_mb = len(file_content) / (1024 * 1024)
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise FileValidationError(filename, f"File too large ({size_mb:.1f} MB). Maximum size is {max_mb:.0f} MB.")
    
    # Check file is not empty
    if len(file_content) == 0:
        raise FileValidationError(filename, "File is empty.")
    
    # Check magic bytes (PDF signature)
    if not file_content[:4].startswith(PDF_MAGIC_BYTES):
        raise FileValidationError(filename, "File is not a valid PDF (invalid magic bytes).")
    
    logger.debug(f"PDF validation passed for {filename} ({len(file_content)} bytes)")


def validate_file_path(file_path: str, allowed_directories: list[str] | None = None) -> str:
    """
    Validate a file path to prevent path traversal attacks.
    
    Args:
        file_path: Path to validate
        allowed_directories: Optional list of allowed base directories
        
    Returns:
        Normalized absolute path
        
    Raises:
        PathTraversalError: If path traversal is detected
        FileValidationError: If path is invalid
    """
    if not file_path or not file_path.strip():
        raise FileValidationError("", "File path cannot be empty.")
    
    # Remove null bytes and other dangerous characters
    file_path = file_path.strip().replace('\x00', '')
    
    # Detect obvious path traversal patterns
    dangerous_patterns = [
        r'\.\.',           # Parent directory
        r'\.\./',          # Parent directory with slash
        r'/\.\./',         # Embedded parent reference
        r'\\\.\.\\',       # Windows parent directory
        r'%2e%2e',         # URL-encoded ..
        r'%252e%252e',     # Double URL-encoded ..
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, file_path, re.IGNORECASE):
            logger.warning(f"Path traversal attempt detected: {file_path}")
            raise PathTraversalError(file_path)
    
    # Normalize the path
    try:
        normalized = os.path.normpath(os.path.abspath(file_path))
    except Exception as e:
        raise FileValidationError(file_path, f"Invalid path: {e}")
    
    # If allowed directories are specified, check that path is within them
    if allowed_directories:
        is_allowed = False
        for allowed_dir in allowed_directories:
            allowed_abs = os.path.normpath(os.path.abspath(allowed_dir))
            if normalized.startswith(allowed_abs):
                is_allowed = True
                break
        
        if not is_allowed:
            logger.warning(f"Path outside allowed directories: {file_path}")
            raise PathTraversalError(file_path)
    
    return normalized


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove potentially dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove directory components
    filename = os.path.basename(filename)
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Replace dangerous characters with underscore
    dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
    filename = re.sub(dangerous_chars, '_', filename)
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        name = name[:max_length - len(ext)]
        filename = name + ext
    
    # Ensure filename is not empty
    if not filename or filename == '.':
        filename = 'unnamed_file'
    
    return filename


def is_valid_image_extension(filename: str) -> bool:
    """Check if filename has a valid image extension."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS
