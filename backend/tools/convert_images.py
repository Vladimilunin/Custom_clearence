import os
import sys
from PIL import Image
from sqlalchemy.orm import Session

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.models import Part

def convert_images_to_webp():
    # Define paths
    # backend/convert_images.py -> backend -> root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "_фото (эскизы) изделий")
    
    print(f"Scanning images in {images_dir}")
    
    if not os.path.exists(images_dir):
        print("Images directory not found!")
        return

    db = SessionLocal()
    count = 0
    converted_count = 0
    
    try:
        # Get all parts with images
        parts = db.query(Part).filter(Part.image_path != None).all()
        print(f"Found {len(parts)} parts with images in DB.")
        
        for part in parts:
            original_filename = part.image_path
            if not original_filename:
                continue
                
            original_path = os.path.join(images_dir, original_filename)
            
            # Check if file exists
            if not os.path.exists(original_path):
                print(f"File not found: {original_path}")
                continue
                
            # Define new filename
            name_part, ext = os.path.splitext(original_filename)
            if ext.lower() == '.webp':
                continue # Already webp
                
            new_filename = f"{name_part}.webp"
            new_path = os.path.join(images_dir, new_filename)
            
            # Convert if not exists
            if not os.path.exists(new_path):
                try:
                    with Image.open(original_path) as img:
                        img.save(new_path, "WEBP")
                    converted_count += 1
                except Exception as e:
                    print(f"Failed to convert {original_filename}: {e}")
                    continue
            
            # Update DB
            part.image_path = new_filename
            count += 1
            
            if count % 50 == 0:
                db.commit()
                print(f"Processed {count} parts...")
        
        db.commit()
        print(f"Finished! Converted {converted_count} new images. Updated {count} DB records.")
        
    finally:
        db.close()

if __name__ == "__main__":
    convert_images_to_webp()
