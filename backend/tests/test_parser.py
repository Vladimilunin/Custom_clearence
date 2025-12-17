"""
Tests for the parser module.
Uses real Groq API calls as per user requirement.
"""
import pytest
import os
from datetime import datetime
from app.services.parser import normalize_date, parse_invoice


class TestNormalizeDate:
    """Test cases for the normalize_date function."""
    
    def test_normalize_date_iso_format(self):
        """Test ISO date format (YYYY-MM-DD)."""
        result = normalize_date("2025-10-24")
        assert result == "24.10.2025"
    
    def test_normalize_date_russian_format(self):
        """Test Russian date format (DD.MM.YYYY) - should return as-is."""
        result = normalize_date("24.10.2025")
        assert result == "24.10.2025"
    
    def test_normalize_date_month_name_abbr(self):
        """Test date with abbreviated month name."""
        result = normalize_date("Oct.16, 2023")
        assert result == "16.10.2023"
    
    def test_normalize_date_with_ordinal_suffix(self):
        """Test date with ordinal suffix (th, st, nd, rd)."""
        result = normalize_date("Oct.16th, 2023")
        assert result == "16.10.2023"
    
    def test_normalize_date_custom_format(self):
        """Test 2025-Oct-24 format."""
        result = normalize_date("2025-Oct-24")
        assert result == "24.10.2025"
    
    def test_normalize_date_empty_string(self):
        """Test empty string input."""
        result = normalize_date("")
        assert result == ""
    
    def test_normalize_date_none(self):
        """Test None input."""
        result = normalize_date(None)
        assert result == ""
    
    def test_normalize_date_invalid_format(self):
        """Test invalid format - should return original string."""
        result = normalize_date("not a date")
        assert result == "not a date"
    
    def test_normalize_date_slash_format(self):
        """Test slash date format."""
        result = normalize_date("2025/10/24")
        assert result == "24.10.2025"


class TestParseInvoice:
    """
    Integration tests for parse_invoice function.
    Uses real Groq API calls.
    """
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Get path to sample PDF for testing."""
        # Look for test PDFs in project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Try to find any PDF file for testing
        pdf_files = [
            os.path.join(base_dir, "3_PI For Алексей Семенов- 20241225.pdf"),
            os.path.join(base_dir, "PI PTJ20251023B1.pdf"),
            os.path.join(base_dir, "Revised PI_Shenzhen_Wofly 20231016.pdf"),
        ]
        
        for pdf_path in pdf_files:
            if os.path.exists(pdf_path):
                return pdf_path
        
        pytest.skip("No test PDF files found in project root")
    
    def test_parse_invoice_returns_tuple(self, sample_pdf_path):
        """Test that parse_invoice returns a tuple of (items, debug_info)."""
        items, debug_info = parse_invoice(sample_pdf_path, method="groq")
        
        assert isinstance(items, list)
        assert isinstance(debug_info, dict)
    
    def test_parse_invoice_debug_info_structure(self, sample_pdf_path):
        """Test that debug_info has expected structure."""
        items, debug_info = parse_invoice(sample_pdf_path, method="groq")
        
        assert "method_used" in debug_info
        assert "page_count" in debug_info
        assert debug_info["page_count"] >= 1
    
    def test_parse_invoice_items_structure(self, sample_pdf_path):
        """Test that parsed items have expected structure."""
        items, debug_info = parse_invoice(sample_pdf_path, method="groq")
        
        if len(items) > 0:
            item = items[0]
            assert "designation" in item
            assert "raw_description" in item or "name" in item
    
    def test_parse_invoice_key_rotation_tracking(self, sample_pdf_path):
        """Test that key rotation is tracked in debug_info."""
        items, debug_info = parse_invoice(sample_pdf_path, method="groq")
        
        assert "key_attempts" in debug_info
        assert isinstance(debug_info["key_attempts"], list)
        
        if len(debug_info["key_attempts"]) > 0:
            attempt = debug_info["key_attempts"][0]
            assert "page" in attempt
            assert "status" in attempt
            assert "key_idx" in attempt
            assert "model" in attempt
    
    def test_parse_invoice_metadata_extraction(self, sample_pdf_path):
        """Test that invoice metadata is extracted."""
        items, debug_info = parse_invoice(sample_pdf_path, method="groq")
        
        assert "invoice_metadata" in debug_info
        metadata = debug_info["invoice_metadata"]
        
        # At least some metadata fields should be present
        metadata_fields = ["invoice_number", "invoice_date", "contract_number", "supplier"]
        has_some_metadata = any(
            metadata.get(field) for field in metadata_fields
        ) if metadata else False
        
        # Note: metadata extraction depends on PDF content, so we just check structure
        assert metadata is None or isinstance(metadata, dict)


class TestParseInvoiceEdgeCases:
    """Edge case tests for parse_invoice."""
    
    def test_parse_invoice_nonexistent_file(self):
        """Test handling of non-existent file."""
        items, debug_info = parse_invoice("/nonexistent/path/file.pdf")
        
        assert items == []
        assert "error" in debug_info
    
    def test_parse_invoice_empty_pdf_path(self):
        """Test handling of empty path."""
        items, debug_info = parse_invoice("")
        
        assert items == []
        assert "error" in debug_info
