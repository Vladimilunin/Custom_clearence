import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/tamozh_db"

async def verify_db():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_async_engine(DATABASE_URL)
        async with engine.connect() as conn:
            print("Connected!")
            # Check if table 'parts' exists
            result = await conn.execute(text("SELECT to_regclass('public.parts');"))
            table_exists = result.scalar()
            
            if table_exists:
                print("Table 'parts' exists.")
                # Try to select from it
                result = await conn.execute(text("SELECT count(*) FROM parts"))
                count = result.scalar()
                print(f"Table 'parts' has {count} rows.")
                
                if count > 0:
                    # Show sample
                    result = await conn.execute(text("SELECT designation, name FROM parts LIMIT 5"))
                    rows = result.fetchall()
                    print("Sample data:")
                    for row in rows:
                        print(row)
            else:
                print("ERROR: Table 'parts' does NOT exist.")
                sys.exit(1)
                
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_db())
