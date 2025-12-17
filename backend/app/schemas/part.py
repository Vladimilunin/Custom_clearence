from pydantic import BaseModel
from typing import Dict, Any, Optional

class PartSchema(BaseModel):
    """Schema for reading part data from database."""
    id: int
    designation: str
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    weight_unit: str | None = "кг"
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None
    manufacturer: str | None = None
    condition: str | None = None
    component_type: str | None = None
    specs: Optional[Dict[str, Any]] = None
    tnved_code: str | None = None
    tnved_description: str | None = None

    class Config:
        from_attributes = True

class PartUpdate(BaseModel):
    """Schema for updating an existing part."""
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    weight_unit: str | None = None
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None
    manufacturer: str | None = None
    condition: str | None = None
    component_type: str | None = None
    specs: Optional[Dict[str, Any]] = None
    tnved_code: str | None = None
    tnved_description: str | None = None

class PartCreate(BaseModel):
    """Schema for creating a new part."""
    designation: str
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    weight_unit: str | None = "кг"
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None
    manufacturer: str | None = None
    condition: str | None = None
    component_type: str | None = None
    specs: Optional[Dict[str, Any]] = None
    tnved_code: str | None = None
    tnved_description: str | None = None

