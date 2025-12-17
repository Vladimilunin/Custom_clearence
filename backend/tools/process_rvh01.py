import sys
import os
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

uploaded_path = r"C:/Users/Владимир/.gemini/antigravity/brain/10833bd8-9624-4c90-a6ef-6aed2c32f2ab/uploaded_image_1763736198184.png"
output_path = "_изображения/RVH-01_render.png"

def process_rvh01():
    print(f"Processing {uploaded_path}...")
    
    try:
        img = Image.open(uploaded_path)
        
        # Create a white square background
        max_dim = max(img.size)
        padding = int(max_dim * 0.05)
        canvas_size = max_dim + 2 * padding
        
        new_img = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))
        
        # Center the original image
        x = (canvas_size - img.width) // 2
        y = (canvas_size - img.height) // 2
        
        if img.mode == 'RGBA':
            new_img.paste(img, (x, y), img)
        else:
            new_img.paste(img, (x, y))
            
        print(f"Saving to {output_path}...")
        new_img.save(output_path)
        
        # Update DB
        part = db.query(Part).filter(Part.designation == "RVH-01").first()
        if part:
            part.image_path = "RVH-01_render.png"
            db.commit()
            print("Database updated for RVH-01.")
        else:
            print("Part RVH-01 not found in DB.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_rvh01()
