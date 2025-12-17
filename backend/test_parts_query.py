import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import text
from app.db.models import Part
from app.core.config import settings
import os

DATABASE_URL = settings.DATABASE_URL
print(f"Testing query on: {DATABASE_URL}")

async def test_query():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("Executing raw SQL query...")
            result = await session.execute(text("SELECT * FROM public.parts LIMIT 1"))
            row = result.first()
            if row:
                print(f"✅ Found part: {row}")
            else:
                print("⚠️ No parts found.")
        except Exception as e:
            print(f"❌ Query failed: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(test_query())
