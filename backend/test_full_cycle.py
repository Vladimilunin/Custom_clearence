import requests
import os
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/v1/invoices"
UPLOAD_URL = f"{BASE_URL}/upload"
GENERATE_URL = f"{BASE_URL}/generate"

# Find a PDF file to test with
PDF_FILE = "Langdi Quotation for  in RMB 20250806-001.pdf"
if not os.path.exists(PDF_FILE):
    # Try looking in parent or other known locations
    potential_paths = [
        "../Langdi Quotation for  in RMB 20250806-001.pdf",
        "d:/Work/_develop/_gen_for_ tamozh/_dev/Langdi Quotation for  in RMB 20250806-001.pdf"
    ]
    for p in potential_paths:
        if os.path.exists(p):
            PDF_FILE = p
            break

if not os.path.exists(PDF_FILE):
    print(f"Error: Could not find test PDF file.")
    sys.exit(1)

print(f"Using PDF: {PDF_FILE}")

# 1. Upload and Parse
print(f"\n[1/2] Uploading and Parsing (Method: openrouter_gemini_free)...")
try:
    with open(PDF_FILE, 'rb') as f:
        files = {'file': f}
        data = {
            'method': 'openrouter_gemini_free', # Or 'auto'
            # 'api_key': '...' # Assuming env var is set in backend
        }
        response = requests.post(UPLOAD_URL, files=files, data=data)
        
    if response.status_code != 200:
        print(f"Upload failed with status {response.status_code}")
        print(response.text)
        sys.exit(1)
        
    upload_data = response.json()
    items = upload_data.get('items', [])
    print(f"Successfully parsed {len(items)} items.")
    for item in items[:3]: # Show first 3
        print(f"  - {item.get('designation')} | {item.get('name')} | {item.get('quantity')}")
        
    if not items:
        print("No items parsed. Cannot proceed to generation.")
        sys.exit(1)

except Exception as e:
    print(f"Exception during upload: {e}")
    sys.exit(1)

# 2. Generate Report
print(f"\n[2/2] Generating Report (Technical Description + Decision 130)...")

gen_payload = {
    "items": items,
    "country_of_origin": "Китай",
    "contract_no": "TEST-CONTRACT",
    "contract_date": "2025-01-01",
    "gen_tech_desc": True,
    "gen_decision_130": True,
    "add_facsimile": True
}

try:
    response = requests.post(GENERATE_URL, json=gen_payload)
    
    if response.status_code == 200:
        output_filename = "full_cycle_test_output.zip"
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        print(f"Success! Report saved to {output_filename}")
        print(f"File size: {os.path.getsize(output_filename)} bytes")
    else:
        print(f"Generation failed with status {response.status_code}")
        print(response.text)
        sys.exit(1)

except Exception as e:
    print(f"Exception during generation: {e}")
    sys.exit(1)
