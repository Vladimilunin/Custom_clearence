import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load cloud config
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.cloud')
load_dotenv(env_path)

def rename_servo():
    print("🚀 Renaming Servo Drive in Cloud DB...")
    
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
            print(f"🔄 Renaming 'Сервопривод ASD-B2' to 'Сервопривод'...")
            update_query = text("""
                UPDATE public.parts 
                SET name = 'Сервопривод' 
                WHERE name = 'Сервопривод ASD-B2'
            """)
            result = conn.execute(update_query)
            
            if result.rowcount > 0:
                print(f"✅ Updated {result.rowcount} rows.")
            else:
                print("⚠️ No rows matched 'Сервопривод ASD-B2'. Trying by designation...")
                # Fallback by designation if name doesn't match exactly
                update_query_fallback = text("""
                    UPDATE public.parts 
                    SET name = 'Сервопривод' 
                    WHERE designation = 'ASD-B2-0421-B'
                """)
                result_fallback = conn.execute(update_query_fallback)
                print(f"✅ Updated {result_fallback.rowcount} rows (by designation).")

            # 2. Verify
            verify_query = text("SELECT designation, name FROM public.parts WHERE designation = 'ASD-B2-0421-B'")
            result = conn.execute(verify_query)
            print("\n🔍 Verification:")
            for row in result:
                print(f"   - {row[0]}: {row[1]}")

    except Exception as e:
        print(f"❌ Error updating DB: {e}")

if __name__ == "__main__":
    rename_servo()
