import requests
import json

def check_api():
    url = "https://backend-service-841188097120.us-central1.run.app/images/R1.003.webp"
    print(f"Fetching {url}...")
    headers = {"Origin": "http://localhost:3000"}
    try:
        response = requests.get(url, stream=True, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        if response.status_code == 200:
            print("✅ Image found!")
        else:
            print("❌ Image not found or error.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
