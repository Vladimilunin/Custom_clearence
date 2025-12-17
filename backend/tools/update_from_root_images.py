import sys
import os
import shutil
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

# List of designations we are interested in (the last 14)
target_designations = [
    "BFC-01-01", "ME-01-02", "T-02", "R11", "MC-01-01", "RVH-01", "RB-02-01",
    "BV3W-01", "UT-01", "Plug-01", "tubing -1/8\"", "MBT-01", "BU-01-0", "BF+FF-01"
]

def update_from_root():
    print("Scanning root directory for images...")
    
    updated = 0
    
    # Get all files in root
    root_files = os.listdir(root_dir)
    
    for designation in target_designations:
        # Try to find a matching file in root
        # The user might have sanitized the filename for "tubing -1/8""
        
        # Possible filenames for this designation
        candidates = [
            f"{designation}.jpg",
            f"{designation}.jpeg",
            f"{designation}.png",
            f"{designation}.webp"
        ]
        
        # Handle special chars in designation for filename matching
        safe_des = designation.replace('"', '').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        if safe_des != designation:
            candidates.append(f"{safe_des}.jpg")
            candidates.append(f"{safe_des}.jpeg")
            candidates.append(f"{safe_des}.png")
            candidates.append(f"{safe_des}.webp")
            
        found_file = None
        for cand in candidates:
            if cand in root_files:
                found_file = cand
                break
        
        if found_file:
            src_path = os.path.join(root_dir, found_file)
            dst_filename = found_file # Keep the same name or standardize? 
            # Let's standardize to safe name to avoid issues
            ext = os.path.splitext(found_file)[1]
            dst_filename = f"{safe_des}{ext}"
            dst_path = os.path.join(images_dir, dst_filename)
            
            print(f"Found {found_file} for {designation}")
            print(f"  Moving to {dst_path}...")
            
            # Move/Copy file
            shutil.copy2(src_path, dst_path)
            
            # Update DB
            part = db.query(Part).filter(Part.designation == designation).first()
            if part:
                part.image_path = dst_filename
                updated += 1
                print(f"  Updated DB for {designation}")
            else:
                print(f"  Part {designation} not found in DB")
                
            # Optional: Delete from root after successful move? 
            # User said "added images", maybe keep them as backup or delete to clean up.
            # I'll leave them for now to be safe, or ask user. 
            # "Clean Up Filesystem" was a previous goal. 
            # I will NOT delete them automatically unless sure.
            
        else:
            print(f"No image found in root for {designation}")

    db.commit()
    print(f"Finished. Updated {updated} parts.")

if __name__ == "__main__":
    try:
        update_from_root()
    except Exception as e:
        print(f"Error: {e}")
