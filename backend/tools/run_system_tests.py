import requests
import os
import sys
import time

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_health():
    log("Testing Backend Health...")
    try:
        resp = requests.get(BASE_URL + "/")
        if resp.status_code == 200:
            log("Backend is UP", "PASS")
            return True
    except Exception as e:
        log(f"Backend is DOWN: {e}", "FAIL")
    return False

def test_parts_crud():
    log("Testing Parts CRUD...")
    # Create
    part_data = {
        "designation": "SYS-TEST-001",
        "name": "System Test Part",
        "material": "Plastic",
        "weight": 0.5,
        "dimensions": "5x5x5",
        "description": "Created by system test"
    }
    resp = requests.post(f"{API_V1}/parts/", json=part_data)
    if resp.status_code == 200:
        log("Part Created", "PASS")
    else:
        log(f"Part Creation Failed: {resp.text}", "FAIL")
        return False
        
    # Read
    resp = requests.get(f"{API_V1}/parts/?search=SYS-TEST-001")
    if resp.status_code == 200 and len(resp.json()) > 0:
        log("Part Found", "PASS")
    else:
        log("Part Not Found", "FAIL")
        return False
    return True

def test_invoice_flow():
    log("Testing Invoice Flow (Upload -> Generate)...")
    
    # Check for sample PDF
    # Resolve path relative to this script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "../../PI PTJ20251023B1.pdf")
    
    if not os.path.exists(pdf_path):
        log(f"Sample PDF not found at {pdf_path}", "WARN")
        return True # Skip if no file
        
    # Upload
    log(f"Uploading {pdf_path}...")
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {'method': 'openrouter_gemini'} # Use openrouter_gemini as requested
        resp = requests.post(f"{API_V1}/invoices/upload", files=files, data=data)
        
    if resp.status_code != 200:
        log(f"Upload Failed: {resp.text}", "FAIL")
        return False
    
    items = resp.json()['items']
    log(f"Upload Success. Found {len(items)} items.", "PASS")
    
    if not items:
        log("No items found to generate report.", "WARN")
        return True
        
    # Generate
    log("Generating Report...")
    gen_req = {
        "items": items,
        "country_of_origin": "Test Country",
        "contract_no": "TEST-123"
    }
    
    resp = requests.post(f"{API_V1}/invoices/generate", json=gen_req)
    
    if resp.status_code == 200:
        log("Report Generated Successfully", "PASS")
        # Save it
        with open("test_report.docx", "wb") as f:
            f.write(resp.content)
        log("Saved test_report.docx", "INFO")
        return True
    else:
        log(f"Report Generation Failed: {resp.text}", "FAIL")
        return False

def main():
    log("Starting System Tests...")
    
    if not test_health():
        sys.exit(1)
        
    if not test_parts_crud():
        sys.exit(1)
        
    if not test_invoice_flow():
        sys.exit(1)
        
    log("All System Tests Passed!", "SUCCESS")

if __name__ == "__main__":
    main()
