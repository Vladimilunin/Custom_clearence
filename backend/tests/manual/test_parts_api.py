import requests
import json

API_URL = "http://localhost:8000/api/v1/parts/"

def test_create_update_part():
    # 1. Create a new part
    part_data = {
        "designation": "TEST-PART-001",
        "name": "Test Part",
        "material": "Steel",
        "weight": 1.5,
        "dimensions": "10x10x10",
        "description": "A test part",
        "image_path": "test.jpg"
    }
    
    print(f"Creating part: {part_data['designation']}")
    response = requests.post(API_URL, json=part_data)
    
    if response.status_code == 200:
        print("Success! Response:", response.json())
    else:
        print("Failed:", response.status_code, response.text)
        return

    # 2. Update the existing part
    update_data = {
        "designation": "TEST-PART-001",
        "name": "Test Part Updated",
        "material": "Aluminum", # Changed material
        "weight": 2.0,          # Changed weight
        "dimensions": "10x10x10",
        "description": "A test part updated",
        "image_path": "test.jpg"
    }
    
    print(f"\nUpdating part: {update_data['designation']}")
    response = requests.post(API_URL, json=update_data)
    
    if response.status_code == 200:
        print("Success! Response:", response.json())
        res_json = response.json()
        if res_json['name'] == "Test Part Updated" and res_json['material'] == "Aluminum":
            print("Verification Passed: Part was updated correctly.")
        else:
            print("Verification Failed: Part was not updated correctly.")
    else:
        print("Failed:", response.status_code, response.text)

if __name__ == "__main__":
    test_create_update_part()
