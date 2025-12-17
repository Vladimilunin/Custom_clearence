from pydantic import BaseModel

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

class PartUpdate(BaseModel):
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None

class PartCreate(BaseModel):
    designation: str
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None
