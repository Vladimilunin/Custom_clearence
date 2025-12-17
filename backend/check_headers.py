import requests
import json

API_URL = "https://backend-service-841188097120.us-central1.run.app"

def check_headers():
    # We need to simulate a generate request. 
    # This requires valid items. 
    # Since we can't easily upload a file to get items, we'll construct a dummy item.
    
    items = [{
        "part_number": "TEST-PART",
        "designation": "Test Designation",
        "description_ru": "Test Part",
        "quantity": 1,
        "price": 10.0,
        "hs_code": "1234567890",
        "manufacturer": "Test Mfg",
        "origin_country": "China",
        "weight_net": 1.0,
        "weight_gross": 1.2,
        "places": 1,
        "carton_number": "1/1"
    }]
    
    payload = {
        "items": items,
        "country_of_origin": "China",
        "contract_no": "TEST-CONTRACT",
        "contract_date": "01.01.2024",
        "supplier": "Test Supplier",
        "invoice_no": "TEST-INVOICE",
        "invoice_date": "01.01.2024",
        "waybill_no": "TEST-WAYBILL",
        "gen_tech_desc": True,
        "gen_non_insurance": False,
        "gen_decision_130": False,
        "add_facsimile": False
    }
    
    print(f"Sending request to {API_URL}/api/v1/invoices/generate...")
    try:
        response = requests.post(
            f"{API_URL}/api/v1/invoices/generate", 
            json=payload, 
            headers={"Origin": "http://localhost:3000"},
            stream=True
        )
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"{k}: {v}")
            
        if response.status_code != 200:
            print("Error response:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_headers()
