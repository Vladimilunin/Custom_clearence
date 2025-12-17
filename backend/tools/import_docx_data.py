import sys
import os
from docx import Document

# Add the current directory to sys.path to make app importable
sys.path.append(os.getcwd())

from app.core.config import settings
from app.db.models import Part
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create sync engine explicitly for this script
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def import_docx(file_path):
    print(f"Reading DOCX file: {file_path}")
    try:
        doc = Document(file_path)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return

    db = SessionLocal()
    count = 0
    
    try:
        for i, table in enumerate(doc.tables):
            data = {}
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if len(cells) >= 2:
                    key = cells[0].lower()
                    val = cells[1]
                    
                    if 'наименование' in key:
                        data['name'] = val
                    elif 'обозначение' in key:
                        data['designation'] = val
                    elif 'размеры' in key:
                        data['dimensions'] = val
            
            if 'designation' in data:
                designation = data['designation']
                name = data.get('name')
                dimensions = data.get('dimensions')
                
                # Find existing part
                existing = db.query(Part).filter(Part.designation == designation).first()
                
                if existing:
                    print(f"Updating {designation}...")
                    if name:
                        existing.name = name
                    if dimensions:
                        existing.dimensions = dimensions
                    count += 1
                else:
                    print(f"Part {designation} not found in DB. Creating...")
                    # Create new part if needed, though user mostly implied updates
                    part = Part(
                        designation=designation,
                        name=name,
                        dimensions=dimensions
                    )
                    db.add(part)
                    count += 1
            
        db.commit()
        print(f"Processed {count} parts from DOCX.")
        
    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    base_dir = r"d:/Work/_develop/_gen_for_ tamozh/_dev/_old/Исходные данные/_для бд"
    docx_path = os.path.join(base_dir, "Техническое описание по 2023668805.docx")
    
    if os.path.exists(docx_path):
        import_docx(docx_path)
    else:
        print(f"File not found: {docx_path}")
