import os
import requests
import json
from dotenv import load_dotenv

# Load env from backend/.env
# Assuming we run from root
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(env_path)

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"Loaded API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:3000",
    "X-Title": "Test Script"
}
payload = {
    "model": "google/gemini-2.0-flash-exp:free",
    "messages": [{"role": "user", "content": "Say hello"}]
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
