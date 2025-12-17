import os
import sys
import asyncio
from dotenv import load_dotenv

# Define paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend
root_dir = os.path.dirname(base_dir) # root
env_cloud_path = os.path.join(base_dir, ".env.cloud")

# Load .env.cloud with override=True BEFORE importing settings
# This ensures cloud credentials take precedence
print(f"Loading cloud config from {env_cloud_path}")
load_dotenv(env_cloud_path, override=True)

# Add backend to sys.path
sys.path.append(base_dir)

from app.services.s3 import s3_service
from app.core.config import settings

def migrate_images():
    images_dir = os.path.join(root_dir, "_изображения")
    
    print(f"Target Bucket: {settings.S3_BUCKET_NAME}")
    print(f"Target Endpoint: {settings.S3_ENDPOINT}")
    print(f"Scanning images in {images_dir}")
    
    if not os.path.exists(images_dir):
        print("Images directory not found!")
        return

    # Create bucket if not exists
    try:
        s3_service.s3_client.create_bucket(Bucket=s3_service.bucket_name)
        print(f"Created/Verified bucket {s3_service.bucket_name}")
    except Exception as e:
        print(f"Bucket check info: {e}")

    uploaded_count = 0
    failed_count = 0
    skipped_count = 0
    
    for filename in os.listdir(images_dir):
        file_path = os.path.join(images_dir, filename)
        if os.path.isfile(file_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                # Check if already exists (optional, but good for resume)
                try:
                    s3_service.s3_client.head_object(Bucket=s3_service.bucket_name, Key=filename)
                    print(f"Skipping {filename} (already exists)")
                    skipped_count += 1
                    continue
                except:
                    pass # Does not exist

                print(f"Uploading {filename}...")
                try:
                    with open(file_path, "rb") as f:
                        res = s3_service.upload_file(f, filename)
                        if res:
                            print(f"Uploaded {filename}")
                            uploaded_count += 1
                        else:
                            print(f"Failed to upload {filename}")
                            failed_count += 1
                except Exception as e:
                    print(f"Error uploading {filename}: {e}")
                    failed_count += 1

    print(f"Migration Finished.")
    print(f"Uploaded: {uploaded_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Failed: {failed_count}")

if __name__ == "__main__":
    migrate_images()
