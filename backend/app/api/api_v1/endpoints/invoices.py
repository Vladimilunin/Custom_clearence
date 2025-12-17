from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Part
from app.services.parser import parse_invoice
from app.services.generator import generate_technical_description
from app.schemas import (
    InvoiceItem,
    InvoiceUploadResponse,
    DebugUploadRequest,
    GenerateRequest,
)
from app.exceptions import FileValidationError, PathTraversalError
from app.utils.validation import validate_pdf_file, validate_file_path, sanitize_filename
import shutil
import os
import tempfile
from typing import List, Any, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed directories for debug_upload endpoint (security whitelist)
ALLOWED_DEBUG_DIRECTORIES = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")),  # Project root
    "/tmp",
    "C:\\Temp",
    os.path.expanduser("~"),
]

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
        logger.debug(f"Parsed {len(parsed_items)} items from invoice")
        
        # Match with DB
        results = []
        
        # Prefetch all parts for fuzzy matching later
        all_parts_result = await db.execute(select(Part))
        all_parts = all_parts_result.scalars().all()
        
        for item in parsed_items:
            designation = item['designation']
            
            # Async query for exact match
            part_result = await db.execute(select(Part).filter(Part.designation == designation))
            part = part_result.scalars().first()
            
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
            
            if part:
                res_item.found_in_db = True
                res_item.name = part.name
                # Only use DB material if not found in invoice
                if not res_item.material:
                    res_item.material = part.material
                res_item.weight = part.weight
                res_item.weight_unit = getattr(part, 'weight_unit', None)
                res_item.dimensions = part.dimensions
                res_item.description = part.description
                res_item.image_path = part.image_path
                
                res_item.condition = part.condition
                # Electronics fields
                res_item.component_type = getattr(part, 'component_type', None)
                res_item.specs = getattr(part, 'specs', None)

                # Determine if electronics
                is_electronics = (res_item.component_type == 'electronics') or \
                                 ('электро' in (res_item.material or '').lower()) or \
                                 (res_item.specs is not None)

                logger.debug(f"Item {designation}: is_electronics={is_electronics}, DB_Manuf={part.manufacturer}")

                # Force overwrite manufacturer from DB ONLY if electronics
                if is_electronics and part.manufacturer:
                    logger.debug(f"Overwriting manufacturer for {designation} to {part.manufacturer}")
                    res_item.manufacturer = part.manufacturer
                
                # Legacy fields
                res_item.current_type = getattr(part, 'current_type', None)
                res_item.input_voltage = getattr(part, 'input_voltage', None)
                res_item.input_current = getattr(part, 'input_current', None)
                res_item.processor = getattr(part, 'processor', None)
                res_item.ram_kb = getattr(part, 'ram_kb', None)
                res_item.rom_mb = getattr(part, 'rom_mb', None)
                res_item.tnved_code = getattr(part, 'tnved_code', None)
                res_item.tnved_description = getattr(part, 'tnved_description', None)
            else:
                # Try Base Part Lookup (e.g. R1.05.00.001-01 -> R1.05.00.001)
                base_part = None
                if '-' in designation:
                    # Try stripping the last suffix
                    base_des = designation.rsplit('-', 1)[0]
                    # Async query for base part
                    base_part_result = await db.execute(select(Part).filter(Part.designation == base_des))
                    base_part = base_part_result.scalars().first()
                
                if base_part:
                    res_item.found_in_db = True
                    res_item.name = base_part.name
                    if not res_item.material:
                        res_item.material = base_part.material
                    res_item.weight = base_part.weight
                    res_item.weight_unit = getattr(base_part, 'weight_unit', None)
                    res_item.dimensions = base_part.dimensions
                    res_item.description = base_part.description
                    res_item.image_path = base_part.image_path
                    res_item.manufacturer = base_part.manufacturer
                    res_item.condition = base_part.condition
                    # Electronics fields
                    res_item.component_type = getattr(base_part, 'component_type', None)
                    res_item.specs = getattr(base_part, 'specs', None)
                    # Legacy fields
                    res_item.current_type = getattr(base_part, 'current_type', None)
                    res_item.input_voltage = getattr(base_part, 'input_voltage', None)
                    res_item.input_current = getattr(base_part, 'input_current', None)
                    res_item.processor = getattr(base_part, 'processor', None)
                    res_item.ram_kb = getattr(base_part, 'ram_kb', None)
                    res_item.rom_mb = getattr(base_part, 'rom_mb', None)
                    res_item.tnved_code = getattr(base_part, 'tnved_code', None)
                    res_item.tnved_description = getattr(base_part, 'tnved_description', None)
                    
                    if not res_item.description:
                        res_item.description = ""
                    res_item.description += f" [Base Match: {base_part.designation}]"
                else:
                    # Fuzzy matching
                    import difflib
                    # Use pre-fetched all_parts
                    all_designations = [p.designation for p in all_parts]
                    
                    matches = difflib.get_close_matches(designation, all_designations, n=1, cutoff=0.8)
                    if matches:
                        fuzzy_des = matches[0]
                        fuzzy_part = next(p for p in all_parts if p.designation == fuzzy_des)
                        
                        res_item.found_in_db = True
                        res_item.name = fuzzy_part.name
                        if not res_item.material:
                            res_item.material = fuzzy_part.material
                        res_item.weight = fuzzy_part.weight
                        res_item.weight_unit = getattr(fuzzy_part, 'weight_unit', None)
                        res_item.dimensions = fuzzy_part.dimensions
                        res_item.description = fuzzy_part.description
                        res_item.image_path = fuzzy_part.image_path
                        res_item.manufacturer = fuzzy_part.manufacturer
                        res_item.condition = fuzzy_part.condition
                        # Electronics fields
                        res_item.component_type = getattr(fuzzy_part, 'component_type', None)
                        res_item.specs = getattr(fuzzy_part, 'specs', None)
                        # Legacy fields
                        res_item.current_type = getattr(fuzzy_part, 'current_type', None)
                        res_item.input_voltage = getattr(fuzzy_part, 'input_voltage', None)
                        res_item.input_current = getattr(fuzzy_part, 'input_current', None)
                        res_item.processor = getattr(fuzzy_part, 'processor', None)
                        res_item.ram_kb = getattr(fuzzy_part, 'ram_kb', None)
                        res_item.rom_mb = getattr(fuzzy_part, 'rom_mb', None)
                        res_item.tnved_code = getattr(fuzzy_part, 'tnved_code', None)
                        res_item.tnved_description = getattr(fuzzy_part, 'tnved_description', None)
                        
                        if not res_item.description:
                            res_item.description = ""
                        res_item.description += f" [Fuzzy Match: {fuzzy_des}]"
            
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
                logger.warning(f"Could not delete temp file {temp_path}: {e}")

@router.post("/upload", response_model=InvoiceUploadResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    method: str = Form("auto"),
    api_key: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads a PDF invoice, parses it (Groq AI), and matches items with the database.
    
    Raises:
        HTTPException 400: Invalid file format
        HTTPException 500: Processing error
    """
    logger.info(f"Received file upload: {file.filename}, method={method}")
    
    # Read file contents
    contents = await file.read()
    
    # Validate PDF file
    try:
        validate_pdf_file(contents, file.filename)
    except FileValidationError as e:
        logger.warning(f"PDF validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    return await process_invoice_contents(contents, safe_filename, method, api_key, db)

@router.post("/debug_upload", response_model=InvoiceUploadResponse)
async def debug_upload_invoice(
    request: DebugUploadRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Debug endpoint to load a file directly from the server's filesystem.
    Useful when OS file dialogs are not available or for automation.
    
    Security: Path traversal protection is enforced.
    
    Raises:
        HTTPException 400: Path traversal detected or invalid file
        HTTPException 404: File not found
        HTTPException 500: Processing error
    """
    # Validate path to prevent path traversal attacks
    try:
        validated_path = validate_file_path(request.file_path, ALLOWED_DEBUG_DIRECTORIES)
    except PathTraversalError as e:
        logger.warning(f"Path traversal attempt blocked: {request.file_path}")
        raise HTTPException(status_code=400, detail="Invalid file path: path traversal not allowed")
    
    if not os.path.exists(validated_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    
    try:
        with open(validated_path, "rb") as f:
            contents = f.read()
        
        # Validate PDF file
        filename = os.path.basename(validated_path)
        try:
            validate_pdf_file(contents, filename)
        except FileValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        safe_filename = sanitize_filename(filename)
        return await process_invoice_contents(contents, safe_filename, request.method, request.api_key, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in debug_upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# GenerateRequest is imported from app.schemas

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
