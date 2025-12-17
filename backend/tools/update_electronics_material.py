import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load cloud config
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.cloud')
load_dotenv(env_path)

def update_materials():
    print("🚀 Updating Electronics Materials in Cloud DB...")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env.cloud")
        return

    # Adjust for sync driver
    db_url = db_url.replace("+asyncpg", "")
    db_url = db_url.replace("ssl=require", "sslmode=require")

    try:
        engine = create_engine(db_url)
        with engine.begin() as conn:
            # 1. Check how many items will be affected
            check_query = text("SELECT count(*) FROM public.parts WHERE component_type = 'electronics'")
            count = conn.execute(check_query).scalar()
            print(f"📊 Found {count} electronics components.")

            if count > 0:
                # 2. Update the material
                update_query = text("""
                    UPDATE public.parts 
                    SET material = 'Пластик, сталь, медь' 
                    WHERE component_type = 'electronics'
                """)
                result = conn.execute(update_query)
                print(f"✅ Updated {result.rowcount} rows.")
            else:
                print("⚠️ No electronics components found to update.")
            
            # 3. Verify the update
            verify_query = text("SELECT designation, name, material FROM public.parts WHERE component_type = 'electronics' LIMIT 5")
            result = conn.execute(verify_query)
            print("\n🔍 Verification (First 5):")
            for row in result:
                print(f"   - {row[0]} ({row[1]}): {row[2]}")

    except Exception as e:
        print(f"❌ Error updating DB: {e}")

if __name__ == "__main__":
    update_materials()
