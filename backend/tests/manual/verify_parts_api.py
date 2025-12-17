import requests
import json

BASE_URL = "http://localhost:8000/api/v1/parts"

def test_parts_api():
    print("1. Fetching parts...")
    response = requests.get(f"{BASE_URL}/?limit=5")
    if response.status_code != 200:
        print(f"Failed to fetch parts: {response.text}")
        return
    
    parts = response.json()
    print(f"Found {len(parts)} parts.")
    if not parts:
        print("No parts found to update. Skipping update test.")
        return

    target_part = parts[0]
    part_id = target_part['id']
    original_name = target_part.get('name')
    print(f"Selected part ID {part_id}: {target_part['designation']} (Name: {original_name})")

    print(f"2. Updating part {part_id}...")
    new_name = "Updated Name Test"
    update_payload = {"name": new_name}
    
    response = requests.put(f"{BASE_URL}/{part_id}", json=update_payload)
    if response.status_code != 200:
        print(f"Failed to update part: {response.text}")
        return
    
    updated_part = response.json()
    print(f"Update response: {updated_part}")
    
    if updated_part['name'] == new_name:
        print("SUCCESS: Part name updated correctly.")
    else:
        print(f"FAILURE: Part name mismatch. Expected {new_name}, got {updated_part['name']}")

    # Revert change
    print("3. Reverting change...")
    revert_payload = {"name": original_name}
    requests.put(f"{BASE_URL}/{part_id}", json=revert_payload)
    print("Reverted.")

if __name__ == "__main__":
    test_parts_api()
