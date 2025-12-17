import requests
import sys

BACKEND_URL = "https://backend-service-841188097120.us-central1.run.app"
FRONTEND_URL = "https://frontend-act3ry31q-vlads-projects-62a7f0a0.vercel.app"

def check_url(url, name):
    try:
        print(f"Checking {name} at {url}...")
        response = requests.get(url, timeout=10)
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
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database connection successful! Retrieved {len(data)} parts.")
            return True
        else:
            print(f"❌ API returned error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API check failed: {e}")
        return False

def main():
    print("--- STARTING DEPLOYMENT VERIFICATION ---")
    
    frontend_ok = check_url(FRONTEND_URL, "Frontend")
    backend_ok = check_url(f"{BACKEND_URL}/docs", "Backend Docs")
    
    db_ok = False
    if backend_ok:
        db_ok = check_api_db()
    
    print("\n--- SUMMARY ---")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ FAILED'}")
    print(f"Backend:  {'✅ OK' if backend_ok else '❌ FAILED'}")
    print(f"Database: {'✅ OK' if db_ok else '❌ FAILED'}")

    if frontend_ok and backend_ok and db_ok:
        print("\n🚀 ALL SYSTEMS GO!")
    else:
        print("\n⚠️ SOME CHECKS FAILED.")

if __name__ == "__main__":
    main()
