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

artifacts_dir = r"C:\Users\Владимир\.gemini\antigravity\brain\10833bd8-9624-4c90-a6ef-6aed2c32f2ab"
images_dir = "_изображения"

# Map prefix -> Designation
mapping = {
    "render_bf_ff_01": "BF+FF-01",
    "render_bu_01_0": "BU-01-0",
    "render_mbt_01": "MBT-01",
    "render_tubing_1_8": "tubing -1/8\"",
    "render_plug_01": "Plug-01",
    "render_ut_01": "UT-01",
    "render_bv3w_01": "BV3W-01",
    "render_rb_02_01": "RB-02-01",
    "render_rvh_01": "RVH-01",
    "render_mc_01_01": "MC-01-01",
    "render_r11": "R11",
    "render_t_02": "T-02",
    "render_me_01_02": "ME-01-02",
    "render_bfc_01_01": "BFC-01-01"
}

def process_images():
    print("Scanning artifacts...")
    files = os.listdir(artifacts_dir)
    
    updated = 0
    for prefix, designation in mapping.items():
        # Find file starting with prefix
        found = None
        for f in files:
            if f.startswith(prefix) and f.endswith(".png"):
                found = f
                break
        
        if found:
            src = os.path.join(artifacts_dir, found)
            # Rename to [Designation].png (sanitize)
            safe_name = designation.replace('"', '').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            dst_name = f"{safe_name}_render.png"
            dst = os.path.join(images_dir, dst_name)
            
            print(f"Copying {found} -> {dst_name}")
            shutil.copy(src, dst)
            
            # Update DB
            part = db.query(Part).filter(Part.designation == designation).first()
            if part:
                part.image_path = dst_name
                updated += 1
                print(f"  Updated DB for {designation}")
            else:
                print(f"  Part {designation} not found in DB")
        else:
            print(f"  Image for {designation} (prefix {prefix}) not found in artifacts")

    db.commit()
    print(f"Finished. Updated {updated} parts.")

if __name__ == "__main__":
    try:
        process_images()
    except Exception as e:
        print(f"Error: {e}")
