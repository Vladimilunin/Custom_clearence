import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Use sync driver for migration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/tamozh_db"

def migrate_db():
    if not DATABASE_URL:
        print("DATABASE_URL not found!")
        return

    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Checking for new columns...")
        
        # Check if manufacturer exists
        try:
            connection.execute(text("ALTER TABLE parts ADD COLUMN manufacturer VARCHAR"))
            print("Added column: manufacturer")
        except Exception as e:
            print(f"Column 'manufacturer' might already exist or error: {e}")
            
        # Check if condition exists
        try:
            connection.execute(text("ALTER TABLE parts ADD COLUMN condition VARCHAR"))
            print("Added column: condition")
        except Exception as e:
            print(f"Column 'condition' might already exist or error: {e}")
            
        connection.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate_db()
