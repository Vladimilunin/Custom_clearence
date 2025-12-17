"""
One-time database update script to fill missing dimensions.
Run: python scripts/update_dimensions.py
"""
import sys
sys.path.insert(0, 'backend')

from app.db.session import sync_engine
from sqlalchemy import text

def update_missing_dimensions():
    with sync_engine.connect() as conn:
        # Update Проставка - Д-16Т, 40х50х3
        conn.execute(text("""
            UPDATE parts 
            SET material = 'Д-16Т', dimensions = '40х50х3'
            WHERE designation LIKE 'R1.001%'
        """))
        print("✓ Updated R1.001 Проставка")
        
        # Update Держатель стакана - Фторопласт, 80х80х80
        conn.execute(text("""
            UPDATE parts 
            SET material = 'Фторопласт', dimensions = '80х80х80'
            WHERE designation LIKE 'R1.002%'
        """))
        print("✓ Updated R1.002 Держатель стакана")
        
        # Update cables with packaging dimensions
        conn.execute(text("""
            UPDATE parts 
            SET dimensions = '140x140x80'
            WHERE designation IN ('ASDB2PW0001', 'ASDB2EN0001')
        """))
        print("✓ Updated ASDB2 cables with packaging dimensions")
        
        conn.commit()
        print("\n✅ All updates committed successfully!")
        
        # Verify
        result = conn.execute(text("""
            SELECT designation, name, material, dimensions 
            FROM parts 
            WHERE dimensions IS NULL OR dimensions = '' OR dimensions = '-'
        """))
        missing = list(result)
        if missing:
            print(f"\n⚠ Still missing dimensions: {len(missing)} parts")
        else:
            print("\n🎉 All parts now have dimensions!")

if __name__ == "__main__":
    update_missing_dimensions()
