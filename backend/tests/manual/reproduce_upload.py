import requests
import os
import json

url = "http://localhost:8000/api/v1/invoices/upload"
file_path = "../Исходные данные/FL202510240002.pdf"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

print(f"Uploading {file_path} to {url}...")

# method = 'gemini'
# method = 'openrouter_qwen'
# method = 'openrouter_gemini'
method = 'openrouter_gemini_free'
# method = 'ocr'

# API Key (optional, can be None if using default/env)
api_key = "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"

data = {
    'method': method,
    'api_key': api_key
}

try:
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files, data=data)
        
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print("Response Text:")
        # print(response.text)
        if 'debug_info' in data:
             print(f"Debug Info: {data['debug_info']}")
             if 'page_count' in data['debug_info']:
                 print(f"Page Count: {data['debug_info']['page_count']}")
        
        if 'items' in data:
            print(f"Found {len(data['items'])} items.")
            for item in data['items']:
                print(f"- {item['designation']}: {item['name']} ({item['material']})")

    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print("Response Text:")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
