import requests
import os
import json

# Configuration
API_URL = "http://localhost:8000/api/v1/invoices"
FILE_PATH = "d:/Work/_develop/_gen_for_ tamozh/_dev/Langdi Quotation for  in RMB 20250806-001.pdf"

def test_generation():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    # 1. Upload and Parse
    print(f"Uploading {FILE_PATH}...")
    with open(FILE_PATH, 'rb') as f:
        files = {'file': f}
        data = {'method': 'openrouter_qwen'} # Use a fast method
        response = requests.post(f"{API_URL}/upload", files=files, data=data)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return

    upload_data = response.json()
    items = upload_data['items']
    metadata = upload_data['metadata']
    print(f"Parsed {len(items)} items.")

    # Common payload data
    base_payload = {
        "items": items,
        "country_of_origin": "Китай",
        "contract_no": metadata.get('invoice_number', 'TEST-CONTRACT'),
        "contract_date": metadata.get('invoice_date', '2023-01-01'),
        "supplier": metadata.get('supplier', 'Test Supplier'),
        "invoice_no": metadata.get('invoice_number', 'TEST-INVOICE'),
        "invoice_date": metadata.get('invoice_date', '2023-01-01'),
    }

    # 2. Test Individual Generations
    tests = [
        ("Technical Description", {"gen_tech_desc": True, "gen_non_insurance": False, "gen_decision_130": False}, "tech_desc.docx"),
        ("Non-Insurance Letter", {"gen_tech_desc": False, "gen_non_insurance": True, "gen_decision_130": False}, "non_insurance.docx"),
        ("Decision 130 Notification", {"gen_tech_desc": False, "gen_non_insurance": False, "gen_decision_130": True}, "decision_130.docx"),
        ("ALL Documents (ZIP)", {"gen_tech_desc": True, "gen_non_insurance": True, "gen_decision_130": True}, "all_docs.zip"),
    ]

    for name, flags, filename in tests:
        print(f"\nTesting generation of: {name}...")
        payload = {**base_payload, **flags}
        
        try:
            gen_response = requests.post(f"{API_URL}/generate", json=payload)
            
            if gen_response.status_code == 200:
                content_type = gen_response.headers.get('Content-Type')
                print(f"Success! Content-Type: {content_type}")
                
                with open(filename, 'wb') as f:
                    f.write(gen_response.content)
                print(f"Saved output to {filename}")
            else:
                print(f"Failed: {gen_response.status_code} - {gen_response.text}")
        except Exception as e:
            print(f"Exception during request: {e}")

if __name__ == "__main__":
    test_generation()
