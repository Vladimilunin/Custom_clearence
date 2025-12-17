import requests
import os

# URL of the deployed backend
API_URL = "https://backend-service-841188097120.us-central1.run.app/api/v1/invoices/upload"
# Path to the test PDF
PDF_PATH = r"d:\Work\_develop\_gen_for_ tamozh\_dev\PI PTJ20251023B1.pdf"

def test_upload():
    if not os.path.exists(PDF_PATH):
        print(f"Error: File not found at {PDF_PATH}")
        return

    print(f"Uploading {PDF_PATH} to {API_URL}...")
    
    try:
        with open(PDF_PATH, 'rb') as f:
            files = {'file': (os.path.basename(PDF_PATH), f, 'application/pdf')}
            data = {'method': 'auto'} # Using 'auto' as default
            
            response = requests.post(API_URL, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            try:
                print("Response JSON:")
                print(response.json())
            except Exception:
                print("Response Text:")
                print(response.text)
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_upload()
