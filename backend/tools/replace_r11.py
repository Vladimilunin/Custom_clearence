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

uploaded_path = r"C:/Users/Владимир/.gemini/antigravity/brain/10833bd8-9624-4c90-a6ef-6aed2c32f2ab/uploaded_image_1763735907138.png"
output_path = "_изображения/R11_render.png"

def process_r11():
    print(f"Processing {uploaded_path}...")
    
    try:
        img = Image.open(uploaded_path)
        
        # Create a white square background
        max_dim = max(img.size)
        # Add a bit of padding (optional, maybe 5%)
        padding = int(max_dim * 0.05)
        canvas_size = max_dim + 2 * padding
        
        new_img = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))
        
        # Center the original image
        x = (canvas_size - img.width) // 2
        y = (canvas_size - img.height) // 2
        
        # Handle transparency if source is RGBA
        if img.mode == 'RGBA':
            new_img.paste(img, (x, y), img)
        else:
            new_img.paste(img, (x, y))
            
        print(f"Saving to {output_path}...")
        new_img.save(output_path)
        
        # Update DB
        part = db.query(Part).filter(Part.designation == "R11").first()
        if part:
            part.image_path = "R11_render.png"
            db.commit()
            print("Database updated for R11.")
        else:
            print("Part R11 not found in DB.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_r11()
