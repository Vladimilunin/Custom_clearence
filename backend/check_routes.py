import requests

BASE_URL = "https://backend-service-841188097120.us-central1.run.app"

endpoints = [
    "/",
    "/docs",
    "/api/v1/parts",
    "/api/v1/invoices/upload",
    "/api/v1/upload/image"
]

for ep in endpoints:
    url = BASE_URL + ep
    try:
        response = requests.get(url)
        print(f"{ep}: {response.status_code}")
    except Exception as e:
        print(f"{ep}: Error {e}")
