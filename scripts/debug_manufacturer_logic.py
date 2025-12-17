import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.models import Part

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/tamozh_db"

async def debug_logic():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    target_designations = ["ASD-B2-0421-B", "ECMA-C20604RS", "ASDB2EN0001"]

    async with async_session() as session:
        for designation in target_designations:
            print(f"\n--- Checking {designation} ---")
            result = await session.execute(select(Part).filter(Part.designation == designation))
            part = result.scalars().first()

            if not part:
                print("Part NOT FOUND in DB")
                continue

            print(f"DB Manufacturer: '{part.manufacturer}'")
            print(f"DB Component Type: '{part.component_type}'")
            print(f"DB Material: '{part.material}'")
            print(f"DB Specs: {part.specs}")

            # Simulate InvoiceItem logic
            res_item_material = part.material
            res_item_component_type = getattr(part, 'component_type', None)
            res_item_specs = getattr(part, 'specs', None)

            # Logic from invoices.py
            is_electronics = (res_item_component_type == 'electronics') or \
                             ('электро' in (res_item_material or '').lower()) or \
                             (res_item_specs is not None)
            
            print(f"Is Electronics: {is_electronics}")

            final_manufacturer = "INVOICE_MANUFACTURER" # Default from invoice
            
            if is_electronics and part.manufacturer:
                final_manufacturer = part.manufacturer
            
            print(f"Final Manufacturer: '{final_manufacturer}'")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(debug_logic())
