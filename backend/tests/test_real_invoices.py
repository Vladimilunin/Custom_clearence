"""
Integration tests with real invoice PDFs.
These tests use real Groq API calls and actual PDF files.

Run with: py -m pytest tests/test_real_invoices.py -v
"""
import pytest
import os
from app.services.parser import parse_invoice


# Get fixtures directory path
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class TestRealInvoiceParsing:
    """
    Integration tests for parsing real invoice PDFs.
    Uses real Groq API calls.
    """
    
    @pytest.fixture(scope="class")
    def sample_invoice_1(self):
        """Path to first sample invoice."""
        path = os.path.join(FIXTURES_DIR, "3_PI For Алексей Семенов- 20241225.pdf")
        if not os.path.exists(path):
            pytest.skip(f"Test PDF not found: {path}")
        return path
    
    @pytest.fixture(scope="class")
    def sample_invoice_2(self):
        """Path to second sample invoice."""
        path = os.path.join(FIXTURES_DIR, "PI PTJ20251023B1.pdf")
        if not os.path.exists(path):
            pytest.skip(f"Test PDF not found: {path}")
        return path
    
    @pytest.fixture(scope="class")
    def sample_invoice_3(self):
        """Path to third sample invoice."""
        path = os.path.join(FIXTURES_DIR, "Revised PI_Shenzhen_Wofly 20231016.pdf")
        if not os.path.exists(path):
            pytest.skip(f"Test PDF not found: {path}")
        return path
    
    @pytest.mark.integration
    def test_parse_invoice_1_returns_items(self, sample_invoice_1):
        """Test parsing first invoice returns items."""
        items, debug_info = parse_invoice(sample_invoice_1, method="groq")
        
        assert isinstance(items, list)
        assert len(items) > 0, "Should find at least one item in invoice"
        
        # Check item structure
        first_item = items[0]
        assert "designation" in first_item
        assert first_item["designation"], "Designation should not be empty"
    
    @pytest.mark.integration
    def test_parse_invoice_1_extracts_metadata(self, sample_invoice_1):
        """Test that metadata is extracted from invoice."""
        items, debug_info = parse_invoice(sample_invoice_1, method="groq")
        
        assert "invoice_metadata" in debug_info
        metadata = debug_info["invoice_metadata"]
        
        # At least one metadata field should be populated
        assert metadata is not None
    
    @pytest.mark.integration
    def test_parse_invoice_2_returns_items(self, sample_invoice_2):
        """Test parsing second invoice returns items."""
        items, debug_info = parse_invoice(sample_invoice_2, method="groq")
        
        assert isinstance(items, list)
        assert len(items) > 0, "Should find at least one item in invoice"
        
        # Debug info should track key attempts
        assert "key_attempts" in debug_info
        assert len(debug_info["key_attempts"]) > 0
    
    @pytest.mark.integration
    def test_parse_invoice_3_multipage(self, sample_invoice_3):
        """Test parsing multi-page invoice."""
        items, debug_info = parse_invoice(sample_invoice_3, method="groq")
        
        assert "page_count" in debug_info
        # Most invoices have at least 1 page
        assert debug_info["page_count"] >= 1
        
        # Items should be collected from all pages
        assert isinstance(items, list)
    
    @pytest.mark.integration
    def test_items_have_valid_structure(self, sample_invoice_1):
        """Test that parsed items have correct structure."""
        items, debug_info = parse_invoice(sample_invoice_1, method="groq")
        
        for item in items:
            # Required fields
            assert "designation" in item
            assert "raw_description" in item or "name" in item
            
            # Designation should be cleaned (no spaces at start/end)
            designation = item.get("designation", "")
            if designation:
                assert designation == designation.strip()
    
    @pytest.mark.integration
    def test_key_rotation_works(self, sample_invoice_2):
        """Test that API key rotation tracking works."""
        items, debug_info = parse_invoice(sample_invoice_2, method="groq")
        
        key_attempts = debug_info.get("key_attempts", [])
        
        # Should have at least one successful attempt
        successful = [a for a in key_attempts if a.get("status") == "success"]
        assert len(successful) > 0, "Should have at least one successful API call"
        
        # Token usage should be tracked
        total_tokens = debug_info.get("token_usage", {}).get("total_tokens", 0)
        assert total_tokens > 0, "Should track token usage"
    
    @pytest.mark.integration
    def test_no_duplicate_items(self, sample_invoice_1):
        """Test that parser doesn't return duplicate items."""
        items, debug_info = parse_invoice(sample_invoice_1, method="groq")
        
        designations = [item.get("designation") for item in items if item.get("designation")]
        unique_designations = set(designations)
        
        # Allow some tolerance for potential duplicates in source document
        # but flag if too many
        duplicate_ratio = len(designations) / max(len(unique_designations), 1)
        assert duplicate_ratio < 1.5, "Too many duplicate items detected"


class TestInvoiceParsingEdgeCases:
    """Edge case tests for invoice parsing."""
    
    @pytest.mark.integration
    def test_corrupted_pdf_handling(self):
        """Test handling of corrupted/invalid PDF."""
        # Create a temporary file with invalid content
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"This is not a valid PDF content")
            temp_path = f.name
        
        try:
            items, debug_info = parse_invoice(temp_path, method="groq")
            
            # Should return empty items with error
            assert items == []
            assert "error" in debug_info
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        items, debug_info = parse_invoice("/nonexistent/invoice.pdf", method="groq")
        
        assert items == []
        assert "error" in debug_info


class TestAPIResponseFormat:
    """Tests for API response format conformance."""
    
    @pytest.mark.integration
    def test_items_serializable(self, sample_invoice_1=None):
        """Test that items can be serialized to JSON."""
        if sample_invoice_1 is None:
            path = os.path.join(FIXTURES_DIR, "3_PI For Алексей Семенов- 20241225.pdf")
            if not os.path.exists(path):
                pytest.skip("Test PDF not found")
            sample_invoice_1 = path
        
        import json
        
        items, debug_info = parse_invoice(sample_invoice_1, method="groq")
        
        # Should be JSON serializable
        try:
            json_str = json.dumps(items, ensure_ascii=False)
            parsed_back = json.loads(json_str)
            assert len(parsed_back) == len(items)
        except (TypeError, json.JSONDecodeError) as e:
            pytest.fail(f"Items are not JSON serializable: {e}")
