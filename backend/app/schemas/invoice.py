"""
Pydantic schemas for Invoice-related API endpoints.

These schemas define request/response models for PDF parsing
and document generation operations.
"""
from pydantic import BaseModel, Field
from typing import List, Any, Dict, Optional


class InvoiceItem(BaseModel):
    """Single item extracted from an invoice."""
    
    designation: str = Field(..., description="Part number/code", example="R1.003")
    raw_description: Optional[str] = Field(None, description="Original description from invoice")
    
    # Fields populated from database
    name: Optional[str] = Field(None, description="Part name in Russian", example="Втулка")
    material: Optional[str] = Field(None, description="Material specification", example="ss316")
    weight: Optional[float] = Field(None, description="Weight value", example=0.5)
    weight_unit: Optional[str] = Field(None, description="Weight unit: 'кг' or 'г'", example="кг")
    dimensions: Optional[str] = Field(None, description="Dimensions in mm", example="100x50x25")
    description: Optional[str] = Field(None, description="Technical description")
    found_in_db: bool = Field(False, description="Whether item was found in database")
    image_path: Optional[str] = Field(None, description="Image filename", example="R1.003.webp")
    parsing_method: Optional[str] = Field(None, description="Method used for parsing")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    condition: Optional[str] = Field(None, description="Condition: 'Новое' or 'Б/У'")
    quantity: Optional[int | str] = Field(1, description="Item quantity")
    price: Optional[float] = Field(None, description="Unit price")
    amount: Optional[float] = Field(None, description="Total amount")
    currency: Optional[str] = Field("USD", description="Currency code")
    
    # Electronics-specific fields
    component_type: Optional[str] = Field(None, description="'electronics' or 'mechanical'")
    specs: Optional[Dict[str, Any]] = Field(None, description="Technical specifications as key-value pairs")
    
    # Legacy fields (deprecated)
    current_type: Optional[str] = None
    input_voltage: Optional[str] = None
    input_current: Optional[str] = None
    processor: Optional[str] = None
    ram_kb: Optional[int] = None
    rom_mb: Optional[int] = None
    tnved_code: Optional[str] = None
    tnved_description: Optional[str] = None
    
    model_config = {"json_schema_extra": {"example": {
        "designation": "R1.003",
        "name": "Втулка установочная",
        "material": "ss316",
        "weight": 0.5,
        "dimensions": "17.7×32×32",
        "found_in_db": True
    }}}


class InvoiceUploadResponse(BaseModel):
    """Response from invoice upload/parsing endpoint."""
    
    items: List[InvoiceItem] = Field(..., description="List of parsed invoice items")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debugging information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Parsing metadata")


class DebugUploadRequest(BaseModel):
    """Request for debug file upload (server-side file path)."""
    
    file_path: str = Field(..., description="Absolute path to PDF on server")
    method: str = Field("groq", description="Parsing method: 'groq'")
    api_key: Optional[str] = Field(None, description="Optional API key override")


class GenerateRequest(BaseModel):
    """Request for generating DOCX report(s)."""
    
    items: List[InvoiceItem] = Field(..., description="Items to include in report")
    country_of_origin: Optional[str] = Field("Китай", description="Country of origin")
    contract_no: Optional[str] = Field(None, description="Contract number")
    contract_date: Optional[str] = Field(None, description="Contract date (DD.MM.YYYY)")
    supplier: Optional[str] = Field("Dongguan City Fangling Precision Mould Co., Ltd.", description="Supplier name")
    invoice_no: Optional[str] = Field(None, description="Invoice number")
    invoice_date: Optional[str] = Field(None, description="Invoice date")
    waybill_no: Optional[str] = Field(None, description="Waybill/AWB number")
    gen_tech_desc: bool = Field(True, description="Generate technical description")
    gen_non_insurance: bool = Field(False, description="Generate non-insurance letter")
    gen_decision_130: bool = Field(False, description="Generate decision 130 notification")
    add_facsimile: bool = Field(False, description="Add facsimile signature")

