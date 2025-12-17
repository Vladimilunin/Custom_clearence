import requests
import os
import json
import re

# Configuration
BACKEND_URL = "https://backend-service-841188097120.us-central1.run.app"
FILE_PATH = r"d:\Work\_develop\_gen_for_ tamozh\_dev\PI PTJ20251023B1.pdf"
IMAGES_DIR = r"d:\Work\_develop\_gen_for_ tamozh\_dev\_изображения"

def find_local_image(designation):
    if not os.path.exists(IMAGES_DIR):
        return None
    
    image_files = os.listdir(IMAGES_DIR)
    
    # 1. Exact match
    candidate = f"{designation}.jpg"
    if candidate in image_files:
        return os.path.join(IMAGES_DIR, candidate)
        
    # 2. Base match (remove suffix like -01)
    # Heuristic: if it ends with a letter or -XX
    if '-' in designation:
        base_des = designation.rsplit('-', 1)[0]
        candidate = f"{base_des}.jpg"
        if candidate in image_files:
            return os.path.join(IMAGES_DIR, candidate)
            
    # 3. Prefix match
    for img in image_files:
        if img.startswith(designation) and img.lower().endswith(('.jpg', '.jpeg', '.png')):
            return os.path.join(IMAGES_DIR, img)
            
    return None

def upload_image_to_backend(local_path):
    url = f"{BACKEND_URL}/api/v1/upload/image"
    try:
        with open(local_path, 'rb') as f:
            files = {'file': (os.path.basename(local_path), f, 'image/jpeg')}
            response = requests.post(url, files=files, timeout=30)
            if response.status_code == 200:
                return response.json().get("filename") # Expecting filename or url
            else:
                print(f"      ⚠️ Image upload failed: {response.text}")
                return None
    except Exception as e:
        print(f"      ⚠️ Image upload error: {e}")
        return None

def restore_db():
    if not os.path.exists(FILE_PATH):
        print(f"❌ File not found: {FILE_PATH}")
        return

    # Step 1: Upload Invoice to get items
    upload_url = f"{BACKEND_URL}/api/v1/invoices/upload"
    print(f"🚀 Uploading {FILE_PATH} to {upload_url}...")

    try:
        with open(FILE_PATH, 'rb') as f:
            files = {'file': (os.path.basename(FILE_PATH), f, 'application/pdf')}
            data = {'method': 'openrouter_gemini_2_5_flash_lite'} 
            
            response = requests.post(upload_url, files=files, data=data, timeout=120)
            
            if response.status_code != 200:
                print(f"❌ Upload Failed: {response.text}")
                return

            result = response.json()
            items = result.get('items', [])
            print(f"✅ Upload Successful! Extracted {len(items)} items.")

            # Step 2: Save items to Parts DB
            parts_url = f"{BACKEND_URL}/api/v1/parts/"
            print(f"💾 Saving items to Parts Database at {parts_url}...")
            
            saved_count = 0
            for item in items:
                designation = item.get('designation')
                
                # Try to find and upload image
                uploaded_image_filename = None
                if designation:
                    local_img_path = find_local_image(designation)
                    if local_img_path:
                        print(f"   📷 Found local image for {designation}: {os.path.basename(local_img_path)}")
                        uploaded_image_filename = upload_image_to_backend(local_img_path)
                        if uploaded_image_filename:
                             print(f"      ✅ Uploaded to R2: {uploaded_image_filename}")
                    else:
                        print(f"   ⚠️ No local image found for {designation}")

                part_data = {
                    "designation": designation,
                    "name": item.get('name'),
                    "material": item.get('material'),
                    "weight": item.get('weight'),
                    "dimensions": item.get('dimensions'),
                    "description": item.get('description'),
                    "image_path": uploaded_image_filename # Now we have the R2 filename!
                }
                
                try:
                    res = requests.post(parts_url, json=part_data, timeout=10)
                    if res.status_code == 200:
                        saved_count += 1
                        print(f"   ✅ Saved Part: {designation}")
                    else:
                        print(f"   ❌ Failed to save part {designation}: {res.text}")
                except Exception as e:
                    print(f"   ❌ Error saving part {designation}: {e}")

            print(f"\n🎉 Finished! Saved {saved_count}/{len(items)} parts to Database.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    restore_db()
