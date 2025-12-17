from app.db.session import SessionLocal
from app.db.models import Part
from sqlalchemy import text

db = SessionLocal()

# Update using raw SQL with IS NULL
result = db.execute(text("""
    UPDATE parts 
    SET component_type = 'fitting' 
    WHERE designation NOT LIKE 'R1%' 
    AND component_type IS NULL
"""))
print(f'Updated {result.rowcount} parts to fitting type')

db.commit()
db.close()
print('Done!')
