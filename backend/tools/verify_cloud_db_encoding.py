import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load cloud config
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.cloud')
load_dotenv(env_path)

def verify_encoding():
    print("🚀 Verifying Cloud DB Encoding...")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env.cloud")
        return

    # Adjust for sync driver
    db_url = db_url.replace("+asyncpg", "")
    db_url = db_url.replace("ssl=require", "sslmode=require")

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Fetch a few rows with potential Cyrillic text
            print("\n🔍 Sampling 'parts' table:")
            result = conn.execute(text("SELECT designation, name, description FROM public.parts LIMIT 5"))
            
            for row in result:
                print(f"---")
                print(f"Designation: {row[0]}")
                print(f"Name:        {row[1]}")
                print(f"Description: {row[2]}")
            
            print("\n✅ Verification query complete.")
            
    except Exception as e:
        print(f"❌ Error connecting to DB: {e}")

if __name__ == "__main__":
    verify_encoding()
