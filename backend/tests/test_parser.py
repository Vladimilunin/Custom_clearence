"""Unit tests for parser.py - Invoice PDF Parser."""
import pytest
from datetime import datetime


class TestNormalizeDate:
    """Tests for the normalize_date function."""

    def test_iso_format(self):
        """Test YYYY-MM-DD format."""
        from app.services.parser import normalize_date
        assert normalize_date("2025-10-24") == "24.10.2025"

    def test_russian_format(self):
        """Test DD.MM.YYYY format (already normalized)."""
        from app.services.parser import normalize_date
        assert normalize_date("24.10.2025") == "24.10.2025"

    def test_slash_format_ymd(self):
        """Test YYYY/MM/DD format."""
        from app.services.parser import normalize_date
        assert normalize_date("2025/10/24") == "24.10.2025"

    def test_slash_format_dmy(self):
        """Test DD/MM/YYYY format."""
        from app.services.parser import normalize_date
        assert normalize_date("24/10/2025") == "24.10.2025"

    def test_month_name_format(self):
        """Test Oct.16, 2023 format."""
        from app.services.parser import normalize_date
        assert normalize_date("Oct.16, 2023") == "16.10.2023"

    def test_full_month_name(self):
        """Test October 16, 2023 format."""
        from app.services.parser import normalize_date
        assert normalize_date("October 16, 2023") == "16.10.2023"

    def test_ordinal_suffix(self):
        """Test date with ordinal suffix (16th, 1st, 2nd, 3rd)."""
        from app.services.parser import normalize_date
        assert normalize_date("Oct.16th, 2023") == "16.10.2023"
        assert normalize_date("October 1st, 2023") == "01.10.2023"
        assert normalize_date("October 2nd, 2023") == "02.10.2023"
        assert normalize_date("October 3rd, 2023") == "03.10.2023"

    def test_dash_month_name_format(self):
        """Test 24-Oct-2025 format."""
        from app.services.parser import normalize_date
        assert normalize_date("24-Oct-2025") == "24.10.2025"

    def test_year_month_day_with_name(self):
        """Test 2025-Oct-24 format."""
        from app.services.parser import normalize_date
        assert normalize_date("2025-Oct-24") == "24.10.2025"

    def test_space_month_name(self):
        """Test 23 Oct 2025 format."""
        from app.services.parser import normalize_date
        assert normalize_date("23 Oct 2025") == "23.10.2025"

    def test_empty_string(self):
        """Test empty string returns empty."""
        from app.services.parser import normalize_date
        assert normalize_date("") == ""

    def test_none_value(self):
        """Test None value returns empty string."""
        from app.services.parser import normalize_date
        assert normalize_date(None) == ""

    def test_unparseable_returns_original(self):
        """Test that unparseable dates return original string."""
        from app.services.parser import normalize_date
        assert normalize_date("gibberish") == "gibberish"

    def test_whitespace_handling(self):
        """Test that whitespace is stripped."""
        from app.services.parser import normalize_date
        assert normalize_date("  2025-10-24  ") == "24.10.2025"


class TestParseInvoiceIntegration:
    """Integration tests for parse_invoice (requires API keys)."""

    # @pytest.mark.skip(reason="Requires valid PDF file and API keys")
    def test_parse_valid_pdf(self):
        """Test parsing a valid PDF invoice using real fixture."""
        from app.services.parser import parse_invoice
        import os
        
        # Use absolute path or relative to project root
        pdf_path = os.path.join(os.path.dirname(__file__), "fixtures", "PI PTJ20251023B1.pdf")
        
        if not os.path.exists(pdf_path):
            pytest.skip(f"Fixture not found: {pdf_path}")
            
        items, debug_info = parse_invoice(pdf_path)
        
        assert isinstance(items, list)
        assert len(items) > 0
        assert "method_used" in debug_info
        assert debug_info["error"] is None

    @pytest.mark.skip(reason="Requires valid PDF file")
    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file."""
        from app.services.parser import parse_invoice
        items, debug_info = parse_invoice("nonexistent.pdf")
        assert items == []
        assert debug_info.get("error") is not None
