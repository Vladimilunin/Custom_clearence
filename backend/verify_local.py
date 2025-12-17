import requests
import sys

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def check_url(url, name):
    try:
        print(f"Checking {name} at {url}...")
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code < 400:
            print(f"✅ {name} is UP!")
            return True
        else:
            print(f"❌ {name} returned error status.")
            return False
    except Exception as e:
        print(f"❌ {name} failed to connect: {e}")
        return False

def check_api_db():
    url = f"{BACKEND_URL}/api/v1/parts/?limit=1"
    try:
        print(f"Checking Database connection via API at {url}...")
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database connection successful! Retrieved {len(data)} parts.")
            if len(data) > 0:
                print(f"   Sample Part: {data[0].get('designation')} - {data[0].get('image_path')}")
            return True
        else:
            print(f"❌ API returned error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API check failed: {e}")
        return False

def main():
    print("--- STARTING LOCAL VERIFICATION ---")
    
    backend_ok = check_url(f"{BACKEND_URL}/docs", "Backend Docs")
    
    db_ok = False
    if backend_ok:
        db_ok = check_api_db()
        
    frontend_ok = check_url(FRONTEND_URL, "Frontend")
    
    print("\n--- SUMMARY ---")
    print(f"Backend:  {'✅ OK' if backend_ok else '❌ FAILED'}")
    print(f"Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ FAILED'}")

    if backend_ok and db_ok and frontend_ok:
        print("\n🚀 ALL SYSTEMS GO!")
    else:
        print("\n⚠️ SOME CHECKS FAILED.")

if __name__ == "__main__":
    main()
