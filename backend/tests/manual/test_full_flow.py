import requests
import json
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

API_URL = "http://localhost:8000/api/v1/invoices"
TEST_PDF_PATH = r"d:\Work\_develop\_gen_for_ tamozh\_dev\BETTERONE-ISA25112201\4_PI For Алексей Семенов- 20241225.pdf"

def test_full_flow():
    print(f"Testing full flow with: {TEST_PDF_PATH}")
    
    # 1. Debug Upload
    print("\n1. Uploading (Debug)...")
    upload_payload = {
        "file_path": TEST_PDF_PATH,
        "method": "groq",
        "api_key": ""
    }
    
    try:
        resp = requests.post(f"{API_URL}/debug_upload", json=upload_payload)
        resp.raise_for_status()
        data = resp.json()
        items = data['items']
        print(f"Success! Found {len(items)} items.")
        
        # Verify new fields in first item
        first_item = items[0]
        print(f"First item sample:")
        print(f"  Designation: {first_item.get('designation')}")
        print(f"  Manufacturer: {first_item.get('manufacturer')}")
        print(f"  Condition: {first_item.get('condition')}")
        print(f"  Image Path: {first_item.get('image_path')}")
        
    except Exception as e:
        print(f"Upload failed: {e}")
        if 'resp' in locals():
            print(resp.text)
        return

    # 2. Generate Report
    print("\n2. Generating Report...")
    
    # Prepare generation payload
    gen_payload = {
        "items": items,
        "country_of_origin": "Китай",
        "contract_no": "TEST-001",
        "contract_date": "2024-12-17",
        "supplier": "Test Supplier",
        "gen_tech_desc": True,
        "gen_non_insurance": False,
        "gen_decision_130": False,
        "add_facsimile": False
    }
    
    try:
        resp = requests.post(f"{API_URL}/generate", json=gen_payload)
        resp.raise_for_status()
        
        output_file = "test_report.docx"
        with open(output_file, "wb") as f:
            f.write(resp.content)
            
        print(f"Success! Report saved to {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
        
    except Exception as e:
        print(f"Generation failed: {e}")
        if 'resp' in locals():
            print(resp.text)

if __name__ == "__main__":
    test_full_flow()
