from app.db.session import SessionLocal
from app.services.importer import import_parts_from_excel
import os

def main():
    db = SessionLocal()
    try:
        # Use absolute path or relative to backend root
        file_path = "../R1.05.00.005-20251121.xls" 
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            # Try absolute path based on finding result
            file_path = "d:/Work/_develop/_gen_for_ tamozh/R1.05.00.005-20251121.xls"
            
        if os.path.exists(file_path):
            import_parts_from_excel(file_path, db)
        else:
            print(f"File still not found: {file_path}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
