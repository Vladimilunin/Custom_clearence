import pandas as pd
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.models import Part
from app.core.config import settings

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

excel_path = "_для бд/2_PI_Shenzhen_Wofly 20231211 (1).xls"
images_dir = "_изображения"

def clean_str(val):
    if pd.isna(val):
        return None
    return str(val).strip()

def import_data():
    print(f"Reading {excel_path}...")
    # Read with header at row 9 (0-indexed)
    df = pd.read_excel(excel_path, header=9)
    
    # Strip column names
    df.columns = df.columns.str.strip()
    print("Columns:", df.columns.tolist())
    
    # Scan images
    image_map = {}
    if os.path.exists(images_dir):
        print(f"Scanning images in {images_dir}...")
        for fname in os.listdir(images_dir):
            # Map filename to itself for now, we'll do fuzzy matching
            image_map[fname] = fname
    
    count = 0
    updated = 0
    
    for index, row in df.iterrows():
        designation = clean_str(row.get('Model'))
        if not designation:
            continue
            
        name = clean_str(row.get('Product Name'))
        description = clean_str(row.get('Description'))
        material = clean_str(row.get('Material'))
        
        # Try to find image
        image_path = None
        
        # 1. Exact match with designation
        # 2. Designation in filename
        # 3. Name in filename
        
        # Let's try to find a file that contains the designation
        # The extracted images are named like "Фитинг гидравлический BFC-01-01.png"
        # So if designation is "BFC-01-01", it should match.
        
        best_match = None
        for fname in image_map:
            if designation in fname:
                best_match = fname
                break
        
        if best_match:
            image_path = best_match
        
        # Check if exists
        existing = db.query(Part).filter(Part.designation == designation).first()
        
        if existing:
            existing.name = name
            existing.description = description
            existing.material = material
            if image_path:
                existing.image_path = image_path
            updated += 1
        else:
            part = Part(
                designation=designation,
                name=name,
                description=description,
                material=material,
                image_path=image_path
            )
            db.add(part)
            count += 1
            
    db.commit()
    print(f"Import finished. Added: {count}, Updated: {updated}")

if __name__ == "__main__":
    try:
        import_data()
    except Exception as e:
        print(f"Error: {e}")
