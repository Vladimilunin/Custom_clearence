import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load cloud config
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.cloud')
load_dotenv(env_path)

def rename_motor():
    print("🚀 Renaming Servo Motor in Cloud DB...")
    
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
            # 1. Update name
            print(f"🔄 Renaming 'Серводвигатель ECMA...' to 'Серводвигатель'...")
            
            # Using ILIKE to match any variation of "Серводвигатель ECMA"
            update_query = text("""
                UPDATE public.parts 
                SET name = 'Серводвигатель' 
                WHERE name ILIKE 'Серводвигатель ECMA%'
            """)
            result = conn.execute(update_query)
            
            if result.rowcount > 0:
                print(f"✅ Updated {result.rowcount} rows.")
            else:
                print("⚠️ No rows matched 'Серводвигатель ECMA%'. Trying by designation...")
                # Fallback by designation
                update_query_fallback = text("""
                    UPDATE public.parts 
                    SET name = 'Серводвигатель' 
                    WHERE designation = 'ECMA-C20604RS'
                """)
                result_fallback = conn.execute(update_query_fallback)
                print(f"✅ Updated {result_fallback.rowcount} rows (by designation).")

            # 2. Verify
            verify_query = text("SELECT designation, name FROM public.parts WHERE designation = 'ECMA-C20604RS'")
            result = conn.execute(verify_query)
            print("\n🔍 Verification:")
            for row in result:
                print(f"   - {row[0]}: {row[1]}")

    except Exception as e:
        print(f"❌ Error updating DB: {e}")

if __name__ == "__main__":
    rename_motor()
