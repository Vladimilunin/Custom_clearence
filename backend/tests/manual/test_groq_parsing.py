import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.parser import parse_invoice

# Load env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(env_path)

async def test_parsing():
    # Use relative path as in the working test
    pdf_path = "PI PTJ20251023B1.pdf"
    
    print(f"Testing parsing of {pdf_path}...")
    try:
        method = "groq"
        
        # The parse_invoice function is NOT async in the current implementation (based on previous edits)
        # But wait, looking at parser.py, it doesn't use async def.
        # However, the test script I edited earlier used `await` which caused an error, so I removed it.
        # So I should call it synchronously.
        
        result, debug_info = parse_invoice(pdf_path, method=method)
        
        print(f"Successfully parsed {len(result)} items.")
        print("-" * 30)
        for i, item in enumerate(result[:3]):
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
    # parse_invoice is synchronous now
    asyncio.run(test_parsing())
