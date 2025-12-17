import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load cloud config
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.cloud')
load_dotenv(env_path)

def update_cable_dimensions():
    print("🚀 Updating Cable Dimensions in Cloud DB...")
    
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
            # 1. Identify cables
            # Targeting specific designations known from previous context or generic name search
            target_designations = ['ASDB2PW0001', 'ASDB2EN0001']
            
            # Also searching by name just in case
            search_query = text("SELECT designation, name FROM public.parts WHERE name ILIKE '%кабель%'")
            print("🔍 Found cables:")
            cables = conn.execute(search_query).fetchall()
            for c in cables:
                print(f"   - {c[0]}: {c[1]}")

            # 2. Update dimensions
            print(f"\n📦 Setting dimensions to '140x140x80' for cables...")
            update_query = text("""
                UPDATE public.parts 
                SET dimensions = '140x140x80' 
                WHERE name ILIKE '%кабель%'
            """)
            result = conn.execute(update_query)
            print(f"✅ Updated {result.rowcount} rows.")
            
            # 3. Verify
            verify_query = text("SELECT designation, name, dimensions FROM public.parts WHERE name ILIKE '%кабель%'")
            result = conn.execute(verify_query)
            print("\n🔍 Verification:")
            for row in result:
                print(f"   - {row[0]}: {row[2]}")

    except Exception as e:
        print(f"❌ Error updating DB: {e}")

if __name__ == "__main__":
    update_cable_dimensions()
