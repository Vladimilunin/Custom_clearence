import os
import sys
import asyncio
from dotenv import load_dotenv

# Load env first
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(env_path)

# Add backend to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from app.services.parser import parse_invoice

async def test_gemini():
    pdf_path = "PI PTJ20251023B1.pdf"
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} not found")
        return

    print(f"Testing parsing of {pdf_path} with OpenRouter Gemini Flash...")
    
    from app.core.config import settings
    print(f"Env Key: {os.getenv('OPENROUTER_API_KEY')[:10]}...")
    print(f"Settings Key: {settings.OPENROUTER_API_KEY[:10]}...")
    
    # Method name from frontend dropdown: openrouter_gemini_2_5_flash_lite
    try:
        items, debug_info = parse_invoice(pdf_path, method="openrouter_gemini_2_5_flash_lite")
        
        print(f"Successfully parsed {len(items)} items.")
        for i, item in enumerate(items[:3]):
            print(f"Item {i+1}:")
            print(f"  Designation: {item.get('designation')}")
            print(f"  Name: {item.get('name')}")
            print(f"  Quantity: {item.get('quantity')}")
            
        if debug_info:
             print("\nDebug Info:")
             print(f"  Method: {debug_info.get('method_used')}")
             print(f"  Error: {debug_info.get('error')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
