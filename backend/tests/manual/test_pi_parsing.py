import sys
import os
import asyncio
from pathlib import Path

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.parser import parse_invoice
from app.core.config import settings

async def test_parsing():
    pdf_path = "PI PTJ20251023B1.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return

    print(f"Testing parsing of {pdf_path}...")
    try:
        # Use a fast model for testing or the default
        method = "siliconflow_qwen" 
        
        # The parse_invoice function is async
        result, debug_info = parse_invoice(pdf_path, method=method)
        
        print(f"Successfully parsed {len(result)} items.")
        print("-" * 30)
        for i, item in enumerate(result[:3]): # Print first 3 items
            print(f"Item {i+1}:")
            print(f"  Designation: {item.get('designation')}")
            print(f"  Name: {item.get('name')}")
            print(f"  Quantity: {item.get('quantity')}")
            print("-" * 30)
            
        if len(result) > 3:
            print(f"... and {len(result) - 3} more items.")
            
    except Exception as e:
        print(f"Parsing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_parsing())
