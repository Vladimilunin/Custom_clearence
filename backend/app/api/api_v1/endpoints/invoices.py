from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Part
from app.services.parser import parse_invoice
from app.services.generator import generate_technical_description
import shutil
import os
import tempfile
import logging
from typing import List, Any, Dict
from app.schemas.invoice import InvoiceItem, InvoiceUploadResponse, DebugUploadRequest, GenerateRequest

logger = logging.getLogger(__name__)

router = APIRouter()

async def _find_part_async(designation: str, db: AsyncSession, all_parts: List[Part]) -> Part | None:
    """Find a part by designation using Exact Match -> Base Part -> Fuzzy Match strategy."""
    if not designation:
        return None
        
    # 1. Exact Match
    # Check in pre-fetched list first to save DB query if possible? 
    # Actually, all_parts might be huge, but iterating in memory is fast.
    # But `process_invoice_contents` does `await db.execute(select(Part).filter(Part.designation == designation))`
    # Let's keep the logic consistent with original but encapsulated.
    
    # 1. Exact Match (DB Query for up-to-date data or use passed all_parts?)
    # Original used DB query for exact match.
    part_result = await db.execute(select(Part).filter(Part.designation == designation))
    part = part_result.scalars().first()
    if part:
        return part, "exact"

    # 2. Base Part Lookup
    if '-' in designation:
        base_des = designation.rsplit('-', 1)[0]
        base_part_result = await db.execute(select(Part).filter(Part.designation == base_des))
        base_part = base_part_result.scalars().first()
        if base_part:
            return base_part, f"base:{base_des}"

    # 3. Fuzzy Matching
    import difflib
    all_designations = [p.designation for p in all_parts]
    matches = difflib.get_close_matches(designation, all_designations, n=1, cutoff=0.8)
    if matches:
        fuzzy_des = matches[0]
        # Find the part object
        fuzzy_part = next((p for p in all_parts if p.designation == fuzzy_des), None)
        if fuzzy_part:
            return fuzzy_part, f"fuzzy:{fuzzy_des}"

    return None, None


def _populate_item_from_part(item: InvoiceItem, part: Part, match_type: str):
    """Populate InvoiceItem fields from a Part database object."""
    item.found_in_db = True
    item.name = part.name
    
    # Only overwrite material if not already present
    if not item.material:
        item.material = part.material
        
    item.weight = part.weight
    item.weight_unit = getattr(part, 'weight_unit', None)
    item.dimensions = part.dimensions
    item.description = part.description
    item.image_path = part.image_path
    
    # Overwrite manufacturer if it's electronics or if not present?
    # Original logic: "Force overwrite manufacturer from DB ONLY if electronics"
    # But also: "res_item.manufacturer = base_part.manufacturer" unconditionally in Base/Fuzzy match block in original code.
    # In Exact match block: only if electronics.
    # Let's preserve specific behavior:
    
    is_electronics = (getattr(part, 'component_type', None) == 'electronics') or \
                     ('электро' in (item.material or '').lower()) or \
                     (getattr(part, 'specs', None) is not None)
                     
    if is_electronics and part.manufacturer:
        item.manufacturer = part.manufacturer
    elif not item.manufacturer:
        # If not electronics, still useful to set if missing?
        # Original exact match block didn't set it if not electronics.
        # But Base/Fuzzy match blocks DID set it unconditionally.
        # This inconsistency suggests we should probably set it if missing.
        item.manufacturer = part.manufacturer

    item.condition = part.condition
    
    # Electronics fields
    item.component_type = getattr(part, 'component_type', None)
    item.specs = getattr(part, 'specs', None)
    
    # Legacy fields
    item.current_type = getattr(part, 'current_type', None)
    item.input_voltage = getattr(part, 'input_voltage', None)
    item.input_current = getattr(part, 'input_current', None)
    item.processor = getattr(part, 'processor', None)
    item.ram_kb = getattr(part, 'ram_kb', None)
    item.rom_mb = getattr(part, 'rom_mb', None)
    item.tnved_code = getattr(part, 'tnved_code', None)
    item.tnved_description = getattr(part, 'tnved_description', None)
    
    # Update description with match info
    if match_type.startswith("base:"):
        base_des = match_type.split(":")[1]
        if not item.description: item.description = ""
        item.description += f" [Base Match: {base_des}]"
    elif match_type.startswith("fuzzy:"):
        fuzzy_des = match_type.split(":")[1]
        if not item.description: item.description = ""
        item.description += f" [Fuzzy Match: {fuzzy_des}]"


async def process_invoice_contents(contents: bytes, filename: str, method: str, api_key: str, db: AsyncSession):
    # Save temp file
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)
    
    with open(temp_path, "wb") as f:
        f.write(contents)
        
    try:
        # Parse invoice
        parsed_items, debug_info = await run_in_threadpool(parse_invoice, pdf_path=temp_path, method=method, api_key=api_key)
        print(f"Parsed items: {parsed_items}")
        
        # Match with DB
        results = []
        
        # Prefetch all parts for fuzzy matching later
        all_parts_result = await db.execute(select(Part))
        all_parts = all_parts_result.scalars().all()
        
        for item in parsed_items:
            designation = item['designation']
            
            res_item = InvoiceItem(
                designation=designation,
                raw_description=item['raw_description'],
                parsing_method=item.get('parsing_method'),
                quantity=item.get('quantity', 1),
                manufacturer=item.get('manufacturer'),
                condition=item.get('condition')
            )
            
            # Prioritize invoice material if found
            if item.get('material'):
                res_item.material = item['material']
            
            # Find in DB (Exact -> Base -> Fuzzy)
            found_part, match_type = await _find_part_async(designation, db, all_parts)
            
            if found_part:
                _populate_item_from_part(res_item, found_part, match_type)
            
            results.append(res_item)
            
        # Extract metadata from debug_info if available
        invoice_metadata = debug_info.get("invoice_metadata") if debug_info else None
        
        # Failsafe Deduplication of results
        unique_results = []
        seen_designations = set()
        for res in results:
            if res.designation not in seen_designations:
                seen_designations.add(res.designation)
                unique_results.append(res)
        results = unique_results

        return InvoiceUploadResponse(items=results, debug_info=debug_info, metadata=invoice_metadata)
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"ERROR in process_invoice_contents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file {temp_path}: {e}")

@router.post("/upload", response_model=InvoiceUploadResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    method: str = Form("auto"),
    api_key: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads a PDF invoice, parses it (Gemini or OCR), and matches items with the database.
    """
    print(f"Received file upload: {file.filename}, method={method}")
    contents = await file.read()
    return await process_invoice_contents(contents, file.filename, method, api_key, db)

@router.post("/debug_upload", response_model=InvoiceUploadResponse)
async def debug_upload_invoice(
    request: DebugUploadRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Debug endpoint to load a file directly from the server's filesystem.
    Useful when OS file dialogs are not available or for automation.
    """
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    
    try:
        with open(request.file_path, "rb") as f:
            contents = f.read()
            
        filename = os.path.basename(request.file_path)
        return await process_invoice_contents(contents, filename, request.method, request.api_key, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/generate")
async def generate_report(
    request: GenerateRequest,
):
    """
    Generate DOCX report(s) from validated items.
    Returns a single DOCX or a ZIP file if multiple documents are requested.
    """
    from app.services.generator import (
        generate_technical_description, 
        generate_non_insurance_letter, 
        generate_decision_130_notification
    )
    import zipfile

    # Convert request items back to Part-like objects
    class SimplePart:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            
    parts_to_gen = []
    for item in request.items:
        parts_to_gen.append(SimplePart(
            designation=item.designation,
            name=item.name or "",
            material=item.material or "",
            weight=item.weight or 0.0,
            weight_unit=item.weight_unit,
            dimensions=item.dimensions or "",
            description=item.description or "",
            image_path=item.image_path,
            manufacturer=item.manufacturer,
            quantity=item.quantity,
            # Electronics fields
            component_type=item.component_type,
            specs=item.specs,
            # Legacy fields
            current_type=item.current_type,
            input_voltage=item.input_voltage,
            input_current=item.input_current,
            processor=item.processor,
            ram_kb=item.ram_kb,
            rom_mb=item.rom_mb,
            tnved_code=item.tnved_code,
            tnved_description=item.tnved_description
        ))
        
    generated_files = []
    
    # 1. Technical Description
    if request.gen_tech_desc:
        tmp_tech = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        await run_in_threadpool(
            generate_technical_description,
            parts_to_gen, 
            tmp_tech,
            country_of_origin=request.country_of_origin,
            contract_no=request.contract_no,
            contract_date=request.contract_date,
            supplier=request.supplier,
            add_facsimile=request.add_facsimile
        )
        generated_files.append({"path": tmp_tech, "name": "Technical_Description.docx"})

    # 2. Non-Insurance Letter
    if request.gen_non_insurance:
        tmp_ins = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        await run_in_threadpool(
            generate_non_insurance_letter,
            parts_to_gen,
            tmp_ins,
            contract_no=request.contract_no or "",
            contract_date=request.contract_date or "",
            invoice_no=request.invoice_no or "",
            invoice_date=request.invoice_date or "",
            waybill_no=request.waybill_no or "",
            add_facsimile=request.add_facsimile
        )
        generated_files.append({"path": tmp_ins, "name": "Non_Insurance_Letter.docx"})

    # 3. Decision 130 Notification
    if request.gen_decision_130:
        tmp_130 = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        await run_in_threadpool(
            generate_decision_130_notification,
            parts_to_gen,
            tmp_130,
            contract_no=request.contract_no or "",
            contract_date=request.contract_date or "",
            invoice_no=request.invoice_no or "",
            invoice_date=request.invoice_date or "",
            add_facsimile=request.add_facsimile
        )
        generated_files.append({"path": tmp_130, "name": "Decision_130_Notification.docx"})

    if not generated_files:
        raise HTTPException(status_code=400, detail="No documents selected for generation")

    # If single file, return it directly
    if len(generated_files) == 1:
        return FileResponse(
            generated_files[0]["path"], 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
            filename=generated_files[0]["name"],
            headers={"Content-Disposition": f'attachment; filename="{generated_files[0]["name"]}"'}
        )
    
    # If multiple files, zip them
    zip_filename = "Documents_Package.zip"
    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
    
    with zipfile.ZipFile(tmp_zip, 'w') as zf:
        for f in generated_files:
            zf.write(f["path"], arcname=f["name"])
            
    return FileResponse(
        tmp_zip,
        media_type='application/zip',
        filename=zip_filename
    )
