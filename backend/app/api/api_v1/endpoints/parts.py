from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Part
from pydantic import BaseModel

router = APIRouter()

class PartSchema(BaseModel):
    id: int
    designation: str
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PartSchema])
async def read_parts(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve parts.
    """
    query = select(Part)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Part.designation.ilike(search_filter)) | 
            (Part.name.ilike(search_filter))
        )
        
    result = await db.execute(query.offset(skip).limit(limit))
    parts = result.scalars().all()
    return parts

class PartUpdate(BaseModel):
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None

@router.put("/{part_id}", response_model=PartSchema)
async def update_part(
    part_id: int,
    part_in: PartUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a part.
    """
    result = await db.execute(select(Part).filter(Part.id == part_id))
    part = result.scalars().first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    update_data = part_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(part, field, value)
        
    db.add(part)
    await db.commit()
    await db.refresh(part)
    return part

class PartCreate(BaseModel):
    designation: str
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None

@router.post("/", response_model=PartSchema)
async def create_part(
    part_in: PartCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new part or update if exists (by designation).
    """
    # Check if exists by designation
    result = await db.execute(select(Part).filter(Part.designation == part_in.designation))
    existing = result.scalars().first()
    
    if existing:
        # Update existing
        update_data = part_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        # Create new
        part = Part(**part_in.dict())
        db.add(part)
        await db.commit()
        await db.refresh(part)
        return part
