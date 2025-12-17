import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, update
from app.db.models import Part

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/tamozh_db"

async def update_part_name():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            # Check if part exists
            result = await session.execute(text("SELECT id, name FROM parts WHERE designation = 'R1.05.00.001'"))
            part = result.fetchone()
            
            if part:
                print(f"Found part: ID={part.id}, Current Name='{part.name}'")
                # Update
                await session.execute(
                    text("UPDATE parts SET name = 'Ось' WHERE designation = 'R1.05.00.001'")
                )
                print("Updated name to 'Ось'")
            else:
                print("Part 'R1.05.00.001' not found. Creating it...")
                # If not found, maybe we should create it? User said "add name", implying update, but if it doesn't exist...
                # Let's assume update for now. If not found, I'll report it.
                # Actually, better to insert if not exists to be helpful? 
                # "R1.05.00.001 добавь наименовапние ось" -> likely means update existing or add new.
                # I'll try to insert if not exists.
                await session.execute(
                    text("INSERT INTO parts (designation, name) VALUES ('R1.05.00.001', 'Ось')")
                )
                print("Created new part 'R1.05.00.001' with name 'Ось'")

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(update_part_name())
