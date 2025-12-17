import os
import sys
from PIL import Image
from sqlalchemy.orm import Session

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.models import Part

def sync_images():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "_фото (эскизы) изделий")
    
    print(f"Scanning images in {images_dir}")
    
    if not os.path.exists(images_dir):
        print("Images directory not found!")
        return

    # 1. Convert all non-WebP images to WebP if missing
    print("Converting images...")
    converted_count = 0
    for filename in os.listdir(images_dir):
        name_part, ext = os.path.splitext(filename)
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            webp_filename = f"{name_part}.webp"
            webp_path = os.path.join(images_dir, webp_filename)
            
            if not os.path.exists(webp_path):
                try:
                    original_path = os.path.join(images_dir, filename)
                    with Image.open(original_path) as img:
                        img.save(webp_path, "WEBP")
                    print(f"Converted {filename} -> {webp_filename}")
                    converted_count += 1
                except Exception as e:
                    print(f"Failed to convert {filename}: {e}")

    print(f"Converted {converted_count} new images.")

    # 2. Update DB for parts missing images or using old extensions
    db = SessionLocal()
    updated_count = 0
    
    try:
        # Get all parts
        parts = db.query(Part).all()
        
        # Build map of available WebP images
        # Key: designation (or filename without ext), Value: filename
        image_map = {}
        for filename in os.listdir(images_dir):
            if filename.lower().endswith('.webp'):
                name_part = os.path.splitext(filename)[0]
                image_map[name_part] = filename
                # Also split by space for "R1.05... Name" style
                parts_split = name_part.split(' ')
                if parts_split:
                    image_map[parts_split[0]] = filename

        for part in parts:
            # If part has no image, or image doesn't exist, or image is not webp
            update_needed = False
            
            current_image = part.image_path
            
            # Check if current image is valid WebP
            if current_image and current_image.lower().endswith('.webp'):
                if os.path.exists(os.path.join(images_dir, current_image)):
                    continue # All good
            
            # Try to find a match
            # 1. Exact match on designation
            candidate = image_map.get(part.designation)
            
            # 2. Prefix match if not found
            if not candidate:
                 for key, val in image_map.items():
                     if key.startswith(part.designation):
                         candidate = val
                         break
            
            if candidate:
                if part.image_path != candidate:
                    print(f"Updating {part.designation}: {part.image_path} -> {candidate}")
                    part.image_path = candidate
                    updated_count += 1
        
        db.commit()
        print(f"Updated {updated_count} DB records.")
        
    finally:
        db.close()

if __name__ == "__main__":
    sync_images()
