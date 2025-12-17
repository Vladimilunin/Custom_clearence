import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.models import Part
from app.core.config import settings

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

images_dir = "_изображения"

def cleanup_images():
    print("Fetching referenced images from DB...")
    parts = db.query(Part).all()
    referenced_images = set()
    for part in parts:
        if part.image_path:
            referenced_images.add(part.image_path)
            
    print(f"Found {len(referenced_images)} unique referenced images.")
    
    print(f"Scanning {images_dir}...")
    if not os.path.exists(images_dir):
        print(f"Directory {images_dir} does not exist.")
        return

    files = os.listdir(images_dir)
    deleted_count = 0
    
    for filename in files:
        # Skip directories if any
        file_path = os.path.join(images_dir, filename)
        if os.path.isdir(file_path):
            continue
            
        if filename not in referenced_images:
            try:
                os.remove(file_path)
                print(f"Deleted: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
        else:
            # print(f"Kept: {filename}")
            pass
            
    print(f"Cleanup finished. Deleted {deleted_count} unreferenced images.")

if __name__ == "__main__":
    cleanup_images()
