"""
Pydantic schemas for request/response validation.
Centralized location for all API schemas.
"""
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# Invoice Schemas
# ============================================================================

class InvoiceItem(BaseModel):
    """Schema for a single invoice item."""

    designation: str = Field(..., description="Part designation/code")
    raw_description: str | None = Field(None, description="Raw description from invoice")

    # Fields from DB
    name: str | None = Field(None, description="Part name")
    material: str | None = Field(None, description="Material")
    weight: float | None = Field(None, ge=0, description="Weight")
    weight_unit: str | None = Field(None, description="Weight unit: 'кг' or 'г'")
    dimensions: str | None = Field(None, description="Dimensions string")
    description: str | None = Field(None, description="Technical description")
    found_in_db: bool = Field(False, description="Whether item was found in database")
    image_path: str | None = Field(None, description="Path to image file")
    parsing_method: str | None = Field(None, description="Method used for parsing")
    manufacturer: str | None = Field(None, description="Manufacturer name")
    condition: str | None = Field(None, description="Condition (New, Refurbished, etc.)")
    quantity: int | str | None = Field(1, description="Quantity")

    # Electronics fields
    component_type: str | None = Field(None, description="Component type: 'electronics' or 'mechanical'")
    specs: dict[str, Any] | None = Field(None, description="Flexible specifications JSON")

    # Legacy fields (kept for backward compatibility)
    current_type: str | None = None
    input_voltage: str | None = None
    input_current: str | None = None
    processor: str | None = None
    ram_kb: int | None = None
    rom_mb: int | None = None
    tnved_code: str | None = None
    tnved_description: str | None = None

    @field_validator('designation')
    @classmethod
    def designation_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Designation cannot be empty')
        return v.strip()


class InvoiceUploadResponse(BaseModel):
    """Response schema for invoice upload."""

    items: list[InvoiceItem]
    debug_info: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class DebugUploadRequest(BaseModel):
    """Request schema for debug upload endpoint."""

    file_path: str = Field(..., description="Path to PDF file on server")
    method: str = Field("groq", description="Parsing method")
    api_key: str | None = Field(None, description="Optional API key override")

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Basic path validation (full security check in endpoint)."""
        if not v or not v.strip():
            raise ValueError('File path cannot be empty')
        # Reject obvious path traversal attempts
        if '..' in v:
            raise ValueError('Path traversal not allowed')
        return v.strip()


class GenerateRequest(BaseModel):
    """Request schema for document generation."""

    items: list[InvoiceItem]
    country_of_origin: str | None = Field("Китай", description="Country of origin")
    contract_no: str | None = Field(None, description="Contract number")
    contract_date: str | None = Field(None, description="Contract date")
    supplier: str | None = Field(
        "Dongguan City Fangling Precision Mould Co., Ltd.",
        description="Supplier name"
    )
    invoice_no: str | None = Field(None, description="Invoice number")
    invoice_date: str | None = Field(None, description="Invoice date")
    waybill_no: str | None = Field(None, description="Waybill number")
    gen_tech_desc: bool = Field(True, description="Generate Technical Description")
    gen_non_insurance: bool = Field(False, description="Generate Non-Insurance Letter")
    gen_decision_130: bool = Field(False, description="Generate Decision 130 Notification")
    add_facsimile: bool = Field(False, description="Add facsimile (stamp and signature)")


# ============================================================================
# Part Schemas
# ============================================================================

class PartBase(BaseModel):
    """Base schema for Part with common fields."""

    name: str | None = None
    material: str | None = None
    weight: float | None = Field(None, ge=0)
    dimensions: str | None = None
    description: str | None = None
    section: str | None = None
    image_path: str | None = None


class PartCreate(PartBase):
    """Schema for creating a new part."""

    designation: str = Field(..., min_length=1, description="Unique part designation")

    @field_validator('designation')
    @classmethod
    def designation_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Designation cannot be empty')
        return v.strip()


class PartUpdate(PartBase):
    """Schema for updating a part."""
    pass


class PartSchema(PartBase):
    """Schema for Part response with ID."""

    id: int
    designation: str

    class Config:
        from_attributes = True


# ============================================================================
# Utility Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str
    error_type: str | None = None
    field: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "1.0.0"
