"""
Tests for the validation utilities.
"""
import pytest
import os

from app.utils.validation import (
    validate_pdf_file,
    validate_file_path,
    sanitize_filename,
    is_valid_image_extension,
)
from app.exceptions import FileValidationError, PathTraversalError


class TestValidatePdfFile:
    """Tests for validate_pdf_file function."""
    
    def test_valid_pdf(self):
        """Test validation of valid PDF content."""
        # Create minimal valid PDF content
        pdf_content = b'%PDF-1.4\n%test minimal pdf'
        
        # Should not raise any exception
        validate_pdf_file(pdf_content, "test.pdf")
    
    def test_invalid_extension(self):
        """Test validation fails for non-PDF extension."""
        pdf_content = b'%PDF-1.4\ntest'
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_pdf_file(pdf_content, "test.docx")
        
        assert "Invalid extension" in str(exc_info.value)
    
    def test_invalid_magic_bytes(self):
        """Test validation fails for non-PDF content."""
        fake_pdf = b'Not a PDF file content'
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_pdf_file(fake_pdf, "test.pdf")
        
        assert "not a valid PDF" in str(exc_info.value)
    
    def test_empty_file(self):
        """Test validation fails for empty file."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_pdf_file(b'', "test.pdf")
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_file_too_large(self):
        """Test validation fails for file exceeding size limit."""
        # Create content larger than 50MB
        large_content = b'%PDF-1.4\n' + b'x' * (51 * 1024 * 1024)
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_pdf_file(large_content, "test.pdf")
        
        assert "too large" in str(exc_info.value).lower()


class TestValidateFilePath:
    """Tests for validate_file_path function."""
    
    def test_valid_path(self):
        """Test validation of valid file path."""
        # Use a path that exists
        valid_path = os.path.abspath(__file__)
        
        result = validate_file_path(valid_path)
        assert result == valid_path
    
    def test_path_traversal_double_dot(self):
        """Test detection of path traversal with .."""
        with pytest.raises(PathTraversalError):
            validate_file_path("../../../etc/passwd")
    
    def test_path_traversal_url_encoded(self):
        """Test detection of URL-encoded path traversal."""
        with pytest.raises(PathTraversalError):
            validate_file_path("%2e%2e/etc/passwd")
    
    def test_path_traversal_windows_style(self):
        """Test detection of Windows-style path traversal."""
        with pytest.raises(PathTraversalError):
            validate_file_path("..\\..\\Windows\\System32")
    
    def test_empty_path(self):
        """Test validation fails for empty path."""
        with pytest.raises(FileValidationError):
            validate_file_path("")
    
    def test_null_bytes(self):
        """Test that null bytes are stripped."""
        path = os.path.abspath(__file__).replace("t", "t\x00")
        # Should either work (after stripping) or raise error, but not crash
        try:
            result = validate_file_path(path)
            # If it works, null bytes should be removed
            assert '\x00' not in result
        except (FileValidationError, PathTraversalError):
            pass  # This is also acceptable
    
    def test_allowed_directories_whitelist(self):
        """Test allowed directories whitelist enforcement."""
        test_file = os.path.abspath(__file__)
        allowed_dir = os.path.dirname(test_file)
        
        # Should work when file is in allowed directory
        result = validate_file_path(test_file, [allowed_dir])
        assert result == test_file
    
    def test_allowed_directories_rejection(self):
        """Test rejection of paths outside allowed directories."""
        test_path = "/some/other/directory/file.pdf"
        allowed_dirs = ["/allowed/only"]
        
        with pytest.raises(PathTraversalError):
            validate_file_path(test_path, allowed_dirs)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""
    
    def test_normal_filename(self):
        """Test sanitization of normal filename."""
        result = sanitize_filename("document.pdf")
        assert result == "document.pdf"
    
    def test_path_components_removed(self):
        """Test that path components are removed."""
        result = sanitize_filename("/path/to/document.pdf")
        assert result == "document.pdf"
        
        result = sanitize_filename("C:\\Users\\test\\document.pdf")
        assert result == "document.pdf"
    
    def test_dangerous_characters_replaced(self):
        """Test that dangerous characters are replaced."""
        result = sanitize_filename("file<>:\"/\\|?*.pdf")
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert '"' not in result
        assert '|' not in result
        assert '?' not in result
        assert '*' not in result
    
    def test_null_bytes_removed(self):
        """Test that null bytes are removed."""
        result = sanitize_filename("file\x00name.pdf")
        assert '\x00' not in result
    
    def test_very_long_filename(self):
        """Test truncation of very long filename."""
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".pdf")
    
    def test_empty_filename(self):
        """Test handling of empty filename."""
        result = sanitize_filename("")
        assert result == "unnamed_file"
    
    def test_cyrillic_filename(self):
        """Test handling of Cyrillic characters."""
        result = sanitize_filename("документ.pdf")
        assert result == "документ.pdf"


class TestIsValidImageExtension:
    """Tests for is_valid_image_extension function."""
    
    def test_valid_extensions(self):
        """Test valid image extensions."""
        assert is_valid_image_extension("image.jpg") == True
        assert is_valid_image_extension("image.jpeg") == True
        assert is_valid_image_extension("image.png") == True
        assert is_valid_image_extension("image.webp") == True
        assert is_valid_image_extension("image.gif") == True
    
    def test_invalid_extensions(self):
        """Test invalid extensions."""
        assert is_valid_image_extension("file.pdf") == False
        assert is_valid_image_extension("file.txt") == False
        assert is_valid_image_extension("file.docx") == False
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert is_valid_image_extension("IMAGE.JPG") == True
        assert is_valid_image_extension("Image.PNG") == True
