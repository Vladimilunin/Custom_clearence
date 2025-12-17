import pytest
import os
from app.services.parser import parse_invoice

# Get absolute path to fixtures directory
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# List of PDF files to test
PDF_FILES = [
    "3_PI For Алексей Семенов- 20241225.pdf",
    "PI PTJ20251023B1.pdf",
    "Revised PI_Shenzhen_Wofly 20231016.pdf"
]

@pytest.mark.parametrize("filename", PDF_FILES)
def test_parse_real_invoice(filename):
    """
    Integration test that runs against real PDF files in the fixtures folder.
    Requires API keys to be set in environment or handled by the parser.
    """
    pdf_path = os.path.join(FIXTURES_DIR, filename)
    
    if not os.path.exists(pdf_path):
        pytest.skip(f"Fixture file not found: {pdf_path}")
        
    print(f"\nTesting parsing of: {filename}")
    
    # Run parsing
    items, debug_info = parse_invoice(pdf_path)
    
    # Basic Assertions
    assert isinstance(items, list), f"Items should be a list for {filename}"
    assert "error" in debug_info
    
    # We expect some items, unless the invoice is empty (unlikely for these samples)
    if debug_info.get("error"):
        pytest.fail(f"Parsing failed with error: {debug_info['error']}")
        
    assert len(items) > 0, f"No items found in {filename}"
    
    # Check structure of first item
    first_item = items[0]
    assert "designation" in first_item
    assert "quantity" in first_item
    
    print(f"Successfully parsed {len(items)} items from {filename}")
