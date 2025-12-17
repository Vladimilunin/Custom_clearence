import requests
import json
import os

API_URL = "http://localhost:8000/api/v1/invoices/generate"
OUTPUT_FILE = "test_report.docx"

def test_generate_report():
    # Mock data simulating what the frontend sends
    payload = {
        "items": [
            {
                "designation": "TEST-001",
                "name": "Test Part 1",
                "material": "Steel",
                "weight": 1.5,
                "dimensions": "10x10x10",
                "description": "Description for part 1",
                "image_path": None,
                "found_in_db": True
            },
            {
                "designation": "TEST-002",
                "name": "Test Part 2",
                "material": "Aluminum",
                "weight": 2.0,
                "dimensions": "20x20x20",
                "description": "Description for part 2",
                "image_path": None,
                "found_in_db": False
            }
        ],
        "country_of_origin": "China",
        "contract_no": "CNT-2024-001",
        "contract_date": "2024-01-01"
    }
    
    print(f"Generating report with metadata: {payload['country_of_origin']}, {payload['contract_no']}")
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            with open(OUTPUT_FILE, "wb") as f:
                f.write(response.content)
            print(f"Success! Report saved to {OUTPUT_FILE}")
            print("Please open the file and verify:")
            print("1. 'Country of Origin: China' in item descriptions.")
            print("2. 'Contract No CNT-2024-001 from 2024-01-01' in the header.")
        else:
            print("Failed:", response.status_code, response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generate_report()
