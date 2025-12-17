import sys
import os

# Add the current directory to sys.path to make app importable
sys.path.append(os.getcwd())

from app.core.config import settings
from app.db.base import Base
from app.services.importer import import_parts_from_excel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create sync engine explicitly for this script
# settings.DATABASE_URL is postgresql+asyncpg://...
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    # Create tables if they don't exist (simple migration)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Import the temp file from root (K1.xlsx copy)
        files_to_import = ["check_k1.xlsx"]
        
        for excel_path in files_to_import:
            if os.path.exists(excel_path):
                import_parts_from_excel(excel_path, db)
            else:
                print(f"File not found: {excel_path}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
