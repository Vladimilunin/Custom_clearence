import os
import sys
import asyncio
from dotenv import load_dotenv

# Load env first
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.s3 import s3_service
from app.core.config import settings

def populate_minio():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    images_dir = os.path.join(base_dir, "_изображения")
    
    print(f"Scanning images in {images_dir}")
    
    if not os.path.exists(images_dir):
        print("Images directory not found!")
        return

    # Create bucket if not exists
    try:
        s3_service.s3_client.create_bucket(Bucket=s3_service.bucket_name)
        print(f"Created bucket {s3_service.bucket_name}")
    except Exception as e:
        # Ignore if exists (or check specific error)
        print(f"Bucket creation info: {e}")

    uploaded_count = 0
    failed_count = 0
    
    for filename in os.listdir(images_dir):
        file_path = os.path.join(images_dir, filename)
        if os.path.isfile(file_path):
            # Check if it's an image
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                print(f"Uploading {filename}...")
                try:
                    with open(file_path, "rb") as f:
                        # Upload to S3
                        # s3_service.upload_file expects a file-like object
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

    print(f"Finished. Uploaded: {uploaded_count}, Failed: {failed_count}")

if __name__ == "__main__":
    populate_minio()
