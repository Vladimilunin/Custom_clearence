"""
Constants for document generation.

Centralizes all magic numbers and configuration values
for DOCX generation, making them easy to maintain.
"""
from docx.shared import Cm, Pt, RGBColor


# Document Margins
class Margins:
    """Document margin settings in centimeters."""
    TOP = Cm(1.27)
    BOTTOM = Cm(1.27)
    LEFT = Cm(1.27)
    RIGHT = Cm(1.27)


# Font Settings
class Fonts:
    """Font configuration for documents."""
    DEFAULT_NAME = "Times New Roman"
    DEFAULT_SIZE = Pt(12)
    TITLE_SIZE = Pt(14)
    SMALL_SIZE = Pt(10)
    HEADER_SIZE = Pt(14)
    
    # Colors (RGB)
    BLACK = RGBColor(0, 0, 0)
    GRAY = RGBColor(100, 100, 100)
    BLUE = RGBColor(0, 0, 255)


# Table Settings
class Tables:
    """Table layout settings for documents."""
    # Column widths in cm
    LABEL_COLUMN_WIDTH = Cm(4)
    VALUE_COLUMN_WIDTH = Cm(12)
    
    # Image dimensions
    IMAGE_WIDTH = Cm(6)
    IMAGE_HEIGHT = Cm(4)
    
    # Min/Max images per row
    IMAGES_PER_ROW = 2


# Page Settings  
class Pages:
    """Page layout settings."""
    WIDTH = Cm(21)  # A4 width
    HEIGHT = Cm(29.7)  # A4 height


# API Configuration
class APIConfig:
    """External API configuration."""
    # Groq
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GROQ_MODELS = [
        "llama-4-scout-17b-16e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct",
    ]
    GROQ_MAX_TOKENS = 4096
    GROQ_TEMPERATURE = 0.1
    
    # Timeouts (seconds)
    API_TIMEOUT = 60
    UPLOAD_TIMEOUT = 120


# File Limits
class FileLimits:
    """File size and type limits."""
    MAX_IMAGE_SIZE_MB = 10
    MAX_PDF_SIZE_MB = 50
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    ALLOWED_PDF_EXTENSIONS = {".pdf"}


# Cache Settings
class CacheSettings:
    """Caching configuration."""
    S3_CACHE_SIZE = 100
    S3_CACHE_TTL = 3600  # 1 hour
    PRESIGNED_URL_EXPIRY = 3600  # 1 hour
