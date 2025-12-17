import sys
import os
import json
# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.parser import parse_invoice

def test_siliconflow():
    pdf_path = "FL202510240002.pdf"
    print(f"Testing SiliconFlow Qwen integration with {pdf_path}...")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found!")
        return

    try:
        # Call parser with real path
        items, debug_info = parse_invoice(pdf_path, method="siliconflow_qwen")
        
        print("\n--- Test Results ---")
        if debug_info.get("error"):
            print(f"FAILED with error: {debug_info['error']}")
        else:
            print("SUCCESS: API request completed.")
            print(f"Method used: {debug_info.get('method_used')}")
            print(f"Token usage: {debug_info.get('token_usage')}")
            print(f"Items found: {len(items)}")
            
            print("\n--- Extracted Items ---")
            print(json.dumps(items, indent=2, ensure_ascii=False))
            
            print("\n--- Metadata ---")
            print(json.dumps(debug_info.get("invoice_metadata"), indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_siliconflow()
