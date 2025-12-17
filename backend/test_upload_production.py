import requests
import os

# Configuration
BACKEND_URL = "https://backend-service-841188097120.us-central1.run.app"
FILE_PATH = r"d:\Work\_develop\_gen_for_ tamozh\_dev\PI PTJ20251023B1.pdf"

def upload_invoice():
    if not os.path.exists(FILE_PATH):
        print(f"❌ File not found: {FILE_PATH}")
        return

    url = f"{BACKEND_URL}/api/v1/invoices/upload"
    print(f"🚀 Uploading {FILE_PATH} to {url}...")

    try:
        with open(FILE_PATH, 'rb') as f:
            files = {'file': (os.path.basename(FILE_PATH), f, 'application/pdf')}
            data = {'method': 'openrouter_gemini_2_5_flash_lite'} # Using default method
            
            response = requests.post(url, files=files, data=data, timeout=60)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload Successful!")
                print(f"📄 Metadata: {result.get('metadata')}")
                items = result.get('items', [])
                print(f"📦 Extracted {len(items)} items.")
                for i, item in enumerate(items[:3]): # Show first 3 items
                    print(f"   - Item {i+1}: {item.get('designation')} | {item.get('name')} | Image: {item.get('image_path')}")
                if len(items) > 3:
                    print(f"   ... and {len(items)-3} more.")
            else:
                print(f"❌ Upload Failed: {response.text}")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    upload_invoice()
