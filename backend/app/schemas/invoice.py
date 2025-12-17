from pydantic import BaseModel
from typing import List, Any, Dict

class InvoiceItem(BaseModel):
    designation: str
    raw_description: str | None = None
    # Fields from DB to be populated
    name: str | None = None
    material: str | None = None
    weight: float | None = None
    weight_unit: str | None = None  # 'кг' или 'г'
    dimensions: str | None = None
    description: str | None = None
    found_in_db: bool = False
    image_path: str | None = None
    parsing_method: str | None = None
    manufacturer: str | None = None
    condition: str | None = None
    quantity: int | str | None = 1
    # Electronics fields
    component_type: str | None = None  # 'electronics' или 'mechanical'
    specs: Dict[str, Any] | None = None  # Гибкие характеристики
    
    # Deprecated/Legacy fields (kept for backward compatibility)
    current_type: str | None = None
    input_voltage: str | None = None
    input_current: str | None = None
    processor: str | None = None
    ram_kb: int | None = None
    rom_mb: int | None = None
    tnved_code: str | None = None
    tnved_description: str | None = None


class InvoiceUploadResponse(BaseModel):
    items: List[InvoiceItem]
    debug_info: Dict[str, Any] | None = None
    metadata: Dict[str, Any] | None = None


class DebugUploadRequest(BaseModel):
    file_path: str
    method: str = "groq"
    api_key: str | None = None


class GenerateRequest(BaseModel):
    items: List[InvoiceItem]
    country_of_origin: str | None = "Китай"
    contract_no: str | None = None
    contract_date: str | None = None
    supplier: str | None = "Dongguan City Fangling Precision Mould Co., Ltd."
    invoice_no: str | None = None
    invoice_date: str | None = None
    waybill_no: str | None = None
    gen_tech_desc: bool = True
    gen_non_insurance: bool = False
    gen_decision_130: bool = False
    add_facsimile: bool = False
