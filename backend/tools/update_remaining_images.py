import sys
import os
import shutil
from PIL import Image
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

root_dir = "d:/Work/_develop/_gen_for_ tamozh"
images_dir = "_изображения"

def crop_to_16_9(img):
    width, height = img.size
    target_ratio = 16 / 9
    current_ratio = width / height
    
    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        offset = (width - new_width) // 2
        return img.crop((offset, 0, offset + new_width, height))
    elif current_ratio < target_ratio:
        new_height = int(width / target_ratio)
        offset = (height - new_height) // 2
        return img.crop((0, offset, width, offset + new_height))
    else:
        return img

def process_remaining():
    print("Processing remaining images...")
    
    tasks = [
        {"file": "RB-02-01.jpg", "designation": "RB-02-01", "dest_name": "RB-02-01.jpg"},
        {"file": "tubing.jpg", "designation": "tubing -1/8\"", "dest_name": "tubing_1_8.jpg"} 
    ]
    
    updated = 0
    
    for task in tasks:
        src_path = os.path.join(root_dir, task["file"])
        dst_path = os.path.join(images_dir, task["dest_name"])
        
        if os.path.exists(src_path):
            print(f"Found {task['file']}...")
            
            # Open, crop, save to dest
            try:
                img = Image.open(src_path)
                cropped = crop_to_16_9(img)
                cropped.save(dst_path)
                print(f"  Cropped and saved to {dst_path}")
                
                # Update DB
                part = db.query(Part).filter(Part.designation == task["designation"]).first()
                if part:
                    part.image_path = task["dest_name"]
                    updated += 1
                    print(f"  Updated DB for {task['designation']}")
                else:
                    print(f"  Part {task['designation']} not found in DB")
                    
            except Exception as e:
                print(f"  Error processing {task['file']}: {e}")
        else:
            print(f"File not found in root: {task['file']}")

    db.commit()
    print(f"Finished. Updated {updated} parts.")

if __name__ == "__main__":
    process_remaining()
