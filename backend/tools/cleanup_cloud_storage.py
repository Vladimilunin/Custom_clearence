import os
import sys
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Define paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend
env_cloud_path = os.path.join(base_dir, ".env.cloud")

# Load .env.cloud
print(f"Loading cloud config from {env_cloud_path}")
load_dotenv(env_cloud_path, override=True)

# Add backend to sys.path
sys.path.append(base_dir)

from app.services.s3 import s3_service
from app.core.config import settings

def cleanup_storage():
    print("🚀 Starting Cloud Storage Cleanup...")
    
    # 1. Get all images from DB
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found!")
        return

    # Force sync driver for this script
    db_url = db_url.replace("+asyncpg", "")
    db_url = db_url.replace("ssl=require", "sslmode=require")

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT image_path FROM public.parts WHERE image_path IS NOT NULL"))
            db_images = {row[0] for row in result}
            print(f"✅ Found {len(db_images)} images referenced in Database.")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return

    # 2. Get all objects from S3
    try:
        s3_objects = []
        paginator = s3_service.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=s3_service.bucket_name)
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    s3_objects.append(obj['Key'])
        
        print(f"✅ Found {len(s3_objects)} objects in Cloud Storage.")
    except Exception as e:
        print(f"❌ S3 error: {e}")
        return

    # 3. Find orphans
    orphans = []
    for obj in s3_objects:
        # Check if object is in DB images
        # DB image_path might be full URL or just filename. 
        # Usually we store just filename or relative path.
        # Let's assume filename match for now.
        is_used = False
        for db_img in db_images:
            if obj in db_img or db_img in obj:
                is_used = True
                break
        
        if not is_used:
            orphans.append(obj)

    print(f"🔍 Found {len(orphans)} orphan files (not in DB).")

    if not orphans:
        print("✨ Storage is clean!")
        return

    # 4. Delete orphans
    print("\nOrphan files:")
    for o in orphans[:10]:
        print(f" - {o}")
    if len(orphans) > 10:
        print(f" ... and {len(orphans) - 10} more.")

    if "--delete" in sys.argv:
        print(f"\n⚠️  Deleting {len(orphans)} files...")
        deleted_count = 0
        for obj in orphans:
            try:
                s3_service.s3_client.delete_object(Bucket=s3_service.bucket_name, Key=obj)
                print(f"Deleted {obj}")
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {obj}: {e}")
        print(f"✅ Deleted {deleted_count} files.")
    else:
        print("\nℹ️  Run with --delete to actually delete these files.")

if __name__ == "__main__":
    cleanup_storage()
