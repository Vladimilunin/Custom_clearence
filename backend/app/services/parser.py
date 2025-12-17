import google.generativeai as genai
import pypdfium2 as pdfium
from PIL import Image
import io
import os
import json
import re
from typing import List, Dict, Tuple
from datetime import datetime

from app.core.config import settings

# Configure Gemini
# In production, use os.environ.get("GEMINI_API_KEY")
DEFAULT_GEMINI_API_KEY = settings.GEMINI_API_KEY

def normalize_date(date_str: str) -> str:
    """
    Normalizes a date string to DD.MM.YYYY format.
    Supports formats like:
    - YYYY-MM-DD
    - DD.MM.YYYY
    - Oct.16th, 2023
    - 2025-Oct-24
    """
    if not date_str:
        return ""
        
    date_str = date_str.strip()
    
    # Common formats
    # Pre-processing for "th", "st", "nd", "rd" in day
    # Remove "th", "st", "nd", "rd" if they follow a digit
    clean_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    
    # Also handle "23th Oct. 2025" -> "23 Oct 2025" (remove dot after month if needed, or handle in formats)
    # The format "%dth %b. %Y" is tricky for strptime directly with suffixes.
    # We already removed suffixes. Now "23 Oct. 2025".
    
    formats = [
        "%Y-%m-%d",       # 2025-10-24
        "%d.%m.%Y",       # 24.10.2025
        "%Y/%m/%d",       # 2025/10/24
        "%d/%m/%Y",       # 24/10/2025
        "%b.%d, %Y",      # Oct.16, 2023
        "%B %d, %Y",      # October 16, 2023
        "%d-%b-%Y",       # 24-Oct-2025
        "%Y-%b-%d",       # 2025-Oct-24
        "%b %d, %Y",      # Oct 16, 2023
        "%d %b. %Y",      # 23 Oct. 2025
        "%d %b %Y",       # 23 Oct 2025
        "%d %B %Y",       # 23 October 2025
    ]
    
    # Try parsing with standard formats
    for fmt in formats:
        try:
            dt = datetime.strptime(clean_str, fmt)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
            
    # Try parsing with "Oct." (abbreviated month with dot) which might not match %b directly in some locales/implementations if strict
    # Manual map for months if needed, but let's try to be robust
    
    return date_str # Return original if parsing fails

def parse_invoice(pdf_path: str, method: str = "auto", api_key: str = None) -> Tuple[List[Dict], Dict]:
    """
    Parses the PDF invoice.
    method: 'auto', 'gemini', or 'ocr'
    api_key: Gemini API key (optional, overrides default)
    """
    items = []
    print(f"Parsing PDF: {pdf_path} with method={method}")
    
    debug_info = {
        "method_used": method,
        "token_usage": None,
        "error": None,
        "page_count": 0
    }

    # Rendering PDF pages
    images = []
    if method in ["gemini", "auto", "siliconflow_qwen"] or method.startswith("openrouter"):
        try:
            print("Rendering PDF pages...")
            pdf = pdfium.PdfDocument(pdf_path)
            for i in range(len(pdf)):
                print(f"Rendering page {i+1}...")
                page = pdf.get_page(i)
                bitmap = page.render(scale=2)
                pil_image = bitmap.to_pil()
                images.append(pil_image)
            pdf.close()
            print(f"Rendered {len(images)} pages.")
            debug_info["page_count"] = len(images)
        except Exception as e:
            print(f"Rendering failed: {e}")
            debug_info["error"] = f"Rendering failed: {e}"
            return [], debug_info

    # Gemini Direct Logic
    if method == "gemini":
        try:
            genai.configure(api_key=api_key or DEFAULT_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')

            all_items = []
            invoice_metadata = {}

            page_prompt = """Extract all line items from this invoice page. Return a valid JSON object with this structure:
{
  "items": [
    {
      "designation": "Part Number/Designation (Alphanumeric code, e.g. R1.003, 5550-0329c)", 
      "description": "Description", 
      "material": "Material", 
      "name": "Part Name (Text description, e.g. Bushing, Plate, Втулка)", 
      "quantity": 0, 
      "unit_price": 0.0, 
      "total_price": 0.0
    }
  ],
  "invoice_number": "Invoice Number (if found on this page)",
  "invoice_date": "Invoice Date (if found on this page)",
  "contract_number": "Contract Number (if found on this page)",
  "contract_date": "Contract Date (if found on this page)",
  "supplier": "Supplier Name (if found on this page)"
}
If a field is not found, return null or empty string. Ensure the JSON is valid.
IMPORTANT: 
1. Do not confuse Designation (code) with Name (text). Designation usually contains numbers and dots/dashes. Name is usually a word.
2. IGNORE rows that are NOT parts, such as: "Shipping cost", "Freight", "Tax", "VAT", "Total", "Subtotal", "Bank charges", "Insurance".
3. IGNORE footer text like "Say total...", "Page x of y".
"""

            for i, img in enumerate(images):
                print(f"Sending page {i+1} to Gemini...")
                response = model.generate_content([page_prompt, img])
                
                try:
                    content_str = response.text
                    # Clean JSON
                    if "```json" in content_str:
                        content_str = content_str.split("```json")[1].split("```")[0]
                    elif "```" in content_str:
                        content_str = content_str.split("```")[1].split("```")[0]
                    
                    data = json.loads(content_str)
                    
                    # Aggregate items
                    page_items = data.get("items", [])
                    if isinstance(page_items, list):
                        all_items.extend(page_items)
                        
                    # Extract metadata from first page
                    if i == 0:
                        invoice_metadata["invoice_number"] = data.get("invoice_number")
                        invoice_metadata["invoice_date"] = normalize_date(data.get("invoice_date"))
                        invoice_metadata["contract_number"] = data.get("contract_number")
                        invoice_metadata["contract_date"] = normalize_date(data.get("contract_date"))
                        invoice_metadata["supplier"] = data.get("supplier")

                except Exception as e:
                    print(f"Error parsing page {i+1} response: {e}")
                    debug_info["error"] = f"Page {i+1} error: {e}"

            # Process items (reuse OpenRouter logic structure)
            # For simplicity, we'll just format them to match the expected output
            for item in all_items:
                items.append({
                    "designation": (item.get("designation") or "").replace(" ", ""),
                    "raw_description": item.get("description") or "",
                    "material": item.get("material") or "",
                    "name": item.get("name") or "",
                    "weight": 0.0,
                    "dimensions": "",
                    "description": "",
                    "parsing_method": "Gemini Direct"
                })
            
            debug_info["invoice_metadata"] = invoice_metadata
            debug_info["method_used"] = "Gemini Direct"
            print(f"Gemini found {len(items)} items.")

        except Exception as e:
            print(f"Gemini parsing failed: {e}")
            debug_info["error"] = f"Gemini failed: {e}"

    # OpenRouter Logic (Actual Implementation)
    if method.startswith("openrouter") or method == "auto":
        try:
            import requests
            import base64
            from io import BytesIO
            
            # Determine model
            if method == "openrouter_gemini":
                model_slug = "google/gemini-2.0-flash-001"
            elif method == "openrouter_gemini_free":
                 model_slug = "google/gemini-2.0-flash-exp:free"
            elif method == "openrouter_gemini_2_5_flash_lite":
                 model_slug = "google/gemini-2.5-flash-lite-preview-09-2025"
            elif method == "openrouter_qwen" or method == "auto":
                model_slug = "qwen/qwen2.5-vl-32b-instruct:free"
            else:
                # Default fallback
                model_slug = "google/gemini-2.0-flash-exp:free"

            # Use settings for API key
            current_api_key = settings.OPENROUTER_API_KEY
            
            # Encode images to base64
            base64_images = []
            for img in images:
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                base64_images.append(img_str)

            print(f"Sending request to OpenRouter ({model_slug})...")
            print(f"DEBUG: Prepared {len(base64_images)} images for OpenRouter.")
            
            headers = {
                "Authorization": f"Bearer {current_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000", # Optional
                "X-Title": "Invoice Parser", # Optional
            }

            # Per-page parsing logic
            all_items = []
            invoice_metadata = {}
            
            page_prompt = """Extract all line items from this invoice page. Return a valid JSON object with this structure:
{
  "items": [
    {
      "designation": "Part Number/Designation (Alphanumeric code, e.g. R1.003, 5550-0329c)", 
      "description": "Description", 
      "material": "Material", 
      "name": "Part Name (Text description, e.g. Bushing, Plate, Втулка)", 
      "quantity": 0, 
      "unit_price": 0.0, 
      "total_price": 0.0
    }
  ],
  "invoice_number": "Invoice Number (if found on this page)",
  "invoice_date": "Invoice Date (if found on this page)",
  "contract_number": "Contract Number (if found on this page)",
  "contract_date": "Contract Date (if found on this page)",
  "supplier": "Supplier Name (if found on this page)"
}
If a field is not found, return null or empty string. Ensure the JSON is valid.
IMPORTANT: 
1. Do not confuse Designation (code) with Name (text). Designation usually contains numbers and dots/dashes. Name is usually a word.
2. IGNORE rows that are NOT parts, such as: "Shipping cost", "Freight", "Tax", "VAT", "Total", "Subtotal", "Bank charges", "Insurance".
3. IGNORE footer text like "Say total...", "Page x of y".
"""


            for i, b64_img in enumerate(base64_images):
                content_payload = [
                    {"type": "text", "text": page_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                    }
                ]

                payload = {
                    "model": model_slug,
                    "messages": [{"role": "user", "content": content_payload}]
                }
                
                try:
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(payload)
                    )
                    
                    if response.status_code == 200:
                        resp_json = response.json()
                        content_str = resp_json['choices'][0]['message']['content']
                        
                        # Clean JSON
                        if "```json" in content_str:
                            content_str = content_str.split("```json")[1].split("```")[0]
                        elif "```" in content_str:
                            content_str = content_str.split("```")[1].split("```")[0]
                        
                        print(f"DEBUG: Raw JSON from OpenRouter (Page {i+1}): {content_str}")
                        
                        data = json.loads(content_str)
                        
                        # Aggregate items
                        page_items = data.get("items", [])
                        if isinstance(page_items, list):
                            all_items.extend(page_items)
                            
                        # Extract metadata from first page
                        if i == 0:
                            invoice_metadata["invoice_number"] = data.get("invoice_number")
                            invoice_metadata["invoice_date"] = normalize_date(data.get("invoice_date"))
                            invoice_metadata["contract_number"] = data.get("contract_number")
                            invoice_metadata["contract_date"] = normalize_date(data.get("contract_date"))
                            invoice_metadata["supplier"] = data.get("supplier")
                            
                        # Capture usage (accumulate?)
                        if 'usage' in resp_json:
                             debug_info["token_usage"] = resp_json['usage']

                    else:
                        print(f"Page {i+1} failed: {response.text}")
                        debug_info["error"] = f"Page {i+1} failed: {response.status_code} - {response.text}"
                        
                except Exception as page_e:
                    print(f"Error parsing page {i+1}: {page_e}")
                    debug_info["error"] = f"Error parsing page {i+1}: {page_e}"

            # Process all items
            debug_info["invoice_metadata"] = invoice_metadata
            debug_info["gemini_model"] = model_slug
            debug_info["all_items_raw"] = all_items # Add this to see raw items in response
            
            print(f"DEBUG: All aggregated items: {json.dumps(all_items, indent=2, ensure_ascii=False)}", flush=True)
            
            # Keywords to exclude
            EXCLUDE_KEYWORDS = ["shipping", "freight", "cost", "tax", "vat", "total", "subtotal", "insurance", "charge", "fee", "доставка", "налог", "итого"]

            for item in all_items:
                # Handle key variations from Qwen
                designation = (item.get("designation") or item.get("part_no") or "").replace(" ", "")
                material = item.get("material") or item.get("material_on_drawing") or item.get("material_on_quotation")
                description = item.get("description") or item.get("remark") or ""
                name = item.get("name") or ""
                
                # Heuristic: Swap Designation and Name if Designation looks like a Name (Cyrillic) and Name is empty
                if designation and not name:
                    # Check for Cyrillic characters
                    if re.search('[а-яА-Я]', designation):
                        print(f"DEBUG: Swapping Designation '{designation}' to Name (Heuristic)")
                        name = designation
                        designation = ""

                # FILTERING LOGIC
                check_str = (designation + " " + name + " " + description).lower()
                if any(kw in check_str for kw in EXCLUDE_KEYWORDS):
                    print(f"DEBUG: Skipping item '{designation}' / '{name}' (Matched exclude keyword)")
                    continue
                
                items.append({
                    "designation": designation,
                    "raw_description": description,
                    "material": material,
                    "name": name,
                    "quantity": item.get("quantity") or 1, # Default to 1 if missing
                    "weight": 0.0,
                    "dimensions": "",
                    "description": "",
                    "parsing_method": f"OpenRouter ({model_slug})"
                })
            
            print(f"OpenRouter found {len(items)} items total.", flush=True)
            debug_info["method_used"] = "OpenRouter"

            # Deduplication Logic
            unique_items = []
            seen_hashes = set()
            
            for item in items:
                # Create a unique hash based on core fields
                des = (item.get("designation") or "").strip().lower()
                mat = (item.get("material") or "").strip().lower()
                
                if not des:
                    item_hash = f"{item.get('raw_description')}|{mat}"
                else:
                    item_hash = f"{des}|{mat}"
                
                if item_hash in seen_hashes:
                    continue
                
                seen_hashes.add(item_hash)
                unique_items.append(item)
            
            items = unique_items


        except Exception as e:
            print(f"Error parsing with OpenRouter: {e}")
            debug_info["error"] = str(e)

    # SiliconFlow Logic
    if method == "siliconflow_qwen":
        try:
            import requests
            import base64
            from io import BytesIO
            
            model_slug = "Qwen/Qwen3-VL-32B-Instruct"
            
            # Use provided API key or fallback (though user provided a specific one, we expect it passed via api_key arg)
            # If api_key arg is empty, we might want to use a default if we had one, but here we rely on the input.
            current_api_key = api_key or "sk-qyhotozwyushoxlrsssdukmhclfrbljpclbsulxuwsiobddh" # Default to user provided key for convenience if not passed
            
            # Encode images to base64
            base64_images = []
            for img in images:
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                base64_images.append(img_str)

            print(f"Sending request to SiliconFlow ({model_slug})...")
            
            headers = {
                "Authorization": f"Bearer {current_api_key}",
                "Content-Type": "application/json"
            }

            # Per-page parsing logic
            all_items = []
            invoice_metadata = {}
            
            page_prompt = """Extract all line items from this invoice page. Return a valid JSON object with this structure:
{
  "items": [
    {
      "designation": "Part Number/Designation (Alphanumeric code, e.g. R1.003, 5550-0329c)", 
      "description": "Description", 
      "material": "Material", 
      "name": "Part Name (Text description, e.g. Bushing, Plate, Втулка)", 
      "quantity": 0, 
      "unit_price": 0.0, 
      "total_price": 0.0
    }
  ],
  "invoice_number": "Invoice Number (if found on this page)",
  "invoice_date": "Invoice Date (if found on this page)",
  "contract_number": "Contract Number (if found on this page)",
  "contract_date": "Contract Date (if found on this page)",
  "supplier": "Supplier Name (if found on this page)"
}
If a field is not found, return null or empty string. Ensure the JSON is valid.
IMPORTANT: 
1. Do not confuse Designation (code) with Name (text). Designation usually contains numbers and dots/dashes. Name is usually a word.
2. IGNORE rows that are NOT parts, such as: "Shipping cost", "Freight", "Tax", "VAT", "Total", "Subtotal", "Bank charges", "Insurance".
3. IGNORE footer text like "Say total...", "Page x of y".
"""

            for i, b64_img in enumerate(base64_images):
                content_payload = [
                    {"type": "text", "text": page_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                    }
                ]

                payload = {
                    "model": model_slug,
                    "messages": [{"role": "user", "content": content_payload}],
                    "stream": False
                }
                
                try:
                    response = requests.post(
                        "https://api.siliconflow.com/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(payload)
                    )
                    
                    if response.status_code == 200:
                        resp_json = response.json()
                        content_str = resp_json['choices'][0]['message']['content']
                        
                        # Clean JSON
                        if "```json" in content_str:
                            content_str = content_str.split("```json")[1].split("```")[0]
                        elif "```" in content_str:
                            content_str = content_str.split("```")[1].split("```")[0]
                        
                        print(f"DEBUG: Raw JSON from SiliconFlow (Page {i+1}): {content_str}")
                        
                        data = json.loads(content_str)
                        
                        # Aggregate items
                        page_items = data.get("items", [])
                        if isinstance(page_items, list):
                            all_items.extend(page_items)
                            
                        # Extract metadata from first page
                        if i == 0:
                            invoice_metadata["invoice_number"] = data.get("invoice_number")
                            invoice_metadata["invoice_date"] = normalize_date(data.get("invoice_date"))
                            invoice_metadata["contract_number"] = data.get("contract_number")
                            invoice_metadata["contract_date"] = normalize_date(data.get("contract_date"))
                            invoice_metadata["supplier"] = data.get("supplier")
                            
                        # Capture usage
                        if 'usage' in resp_json:
                             debug_info["token_usage"] = resp_json['usage']

                    else:
                        print(f"Page {i+1} failed: {response.text}")
                        debug_info["error"] = f"Page {i+1} failed: {response.status_code} - {response.text}"
                        
                except Exception as page_e:
                    print(f"Error parsing page {i+1}: {page_e}")
                    debug_info["error"] = f"Error parsing page {i+1}: {page_e}"

            # Process all items
            debug_info["invoice_metadata"] = invoice_metadata
            debug_info["gemini_model"] = model_slug
            debug_info["all_items_raw"] = all_items
            
            print(f"DEBUG: All aggregated items: {json.dumps(all_items, indent=2, ensure_ascii=False)}", flush=True)
            
            # Keywords to exclude
            EXCLUDE_KEYWORDS = ["shipping", "freight", "cost", "tax", "vat", "total", "subtotal", "insurance", "charge", "fee", "доставка", "налог", "итого"]

            for item in all_items:
                # Handle key variations
                designation = (item.get("designation") or item.get("part_no") or "").replace(" ", "")
                material = item.get("material") or item.get("material_on_drawing") or item.get("material_on_quotation")
                description = item.get("description") or item.get("remark") or ""
                name = item.get("name") or ""
                
                # Heuristic: Swap Designation and Name if Designation looks like a Name (Cyrillic) and Name is empty
                if designation and not name:
                    if re.search('[а-яА-Я]', designation):
                        name = designation
                        designation = ""

                # FILTERING LOGIC
                check_str = (designation + " " + name + " " + description).lower()
                if any(kw in check_str for kw in EXCLUDE_KEYWORDS):
                    continue
                
                items.append({
                    "designation": designation,
                    "raw_description": description,
                    "material": material,
                    "name": name,
                    "quantity": item.get("quantity") or 1,
                    "weight": 0.0,
                    "dimensions": "",
                    "description": "",
                    "parsing_method": f"SiliconFlow ({model_slug})"
                })
            
            print(f"SiliconFlow found {len(items)} items total.", flush=True)
            debug_info["method_used"] = "SiliconFlow"

            # Deduplication Logic
            unique_items = []
            seen_hashes = set()
            
            for item in items:
                des = (item.get("designation") or "").strip().lower()
                mat = (item.get("material") or "").strip().lower()
                
                if not des:
                    item_hash = f"{item.get('raw_description')}|{mat}"
                else:
                    item_hash = f"{des}|{mat}"
                
                if item_hash in seen_hashes:
                    continue
                
                seen_hashes.add(item_hash)
                unique_items.append(item)
            
            items = unique_items


        except Exception as e:
            print(f"Error parsing with SiliconFlow: {e}")
            debug_info["error"] = str(e)

    # DeepSeek Logic
    # DeepSeek Logic
    if method == "deepseek_v3":
        try:
            import requests
            import pdfplumber
            
            # User indicated "DeepSeek-V3.2-Exp is the non-thinking mode", usually mapped to 'deepseek-chat'
            model_slug = "deepseek-chat" 
            
            current_api_key = api_key or "sk-cdd6c308faa04345b336ef9de4824300"
            
            print(f"Extracting text for DeepSeek ({model_slug})...")
            
            # Extract text from PDF
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n\n"
            
            print(f"Extracted {len(full_text)} characters.")

            headers = {
                "Authorization": f"Bearer {current_api_key}",
                "Content-Type": "application/json"
            }

            all_items = []
            invoice_metadata = {}
            
            prompt = f"""Extract all line items from the following invoice text. Return a valid JSON object with this structure:
{{
  "items": [
    {{
      "designation": "Part Number/Designation (Alphanumeric code, e.g. R1.003, 5550-0329c)", 
      "description": "Description", 
      "material": "Material", 
      "name": "Part Name (Text description, e.g. Bushing, Plate, Втулка)", 
      "quantity": 0, 
      "unit_price": 0.0, 
      "total_price": 0.0
    }}
  ],
  "invoice_number": "Invoice Number",
  "invoice_date": "Invoice Date",
  "contract_number": "Contract Number",
  "contract_date": "Contract Date",
  "supplier": "Supplier Name"
}}
If a field is not found, return null or empty string. Ensure the JSON is valid.
IMPORTANT: 
1. Do not confuse Designation (code) with Name (text). Designation usually contains numbers and dots/dashes. Name is usually a word.
2. IGNORE rows that are NOT parts, such as: "Shipping cost", "Freight", "Tax", "VAT", "Total", "Subtotal", "Bank charges", "Insurance".

INVOICE TEXT:
{full_text}
"""

            payload = {
                "model": model_slug,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            
            try:
                response = requests.post(
                    "https://api.deepseek.com/chat/completions",
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                if response.status_code == 200:
                    resp_json = response.json()
                    content_str = resp_json['choices'][0]['message']['content']
                    
                    # Clean JSON
                    if "```json" in content_str:
                        content_str = content_str.split("```json")[1].split("```")[0]
                    elif "```" in content_str:
                        content_str = content_str.split("```")[1].split("```")[0]
                    
                    print(f"DEBUG: Raw JSON from DeepSeek: {content_str}")
                    
                    data = json.loads(content_str)
                    
                    # Aggregate items
                    page_items = data.get("items", [])
                    if isinstance(page_items, list):
                        all_items.extend(page_items)
                        
                    # Extract metadata
                    invoice_metadata["invoice_number"] = data.get("invoice_number")
                    invoice_metadata["invoice_date"] = normalize_date(data.get("invoice_date"))
                    invoice_metadata["contract_number"] = data.get("contract_number")
                    invoice_metadata["contract_date"] = normalize_date(data.get("contract_date"))
                    invoice_metadata["supplier"] = data.get("supplier")
                        
                    # Capture usage
                    if 'usage' in resp_json:
                            debug_info["token_usage"] = resp_json['usage']

                else:
                    print(f"DeepSeek request failed: {response.text}")
                    debug_info["error"] = f"DeepSeek request failed: {response.status_code} - {response.text}"
                    
            except Exception as page_e:
                print(f"Error parsing with DeepSeek: {page_e}")
                debug_info["error"] = f"Error parsing with DeepSeek: {page_e}"

            # Process all items
            debug_info["invoice_metadata"] = invoice_metadata
            debug_info["gemini_model"] = model_slug
            debug_info["all_items_raw"] = all_items
            
            print(f"DEBUG: All aggregated items: {json.dumps(all_items, indent=2, ensure_ascii=False)}", flush=True)
            
            # Keywords to exclude
            EXCLUDE_KEYWORDS = ["shipping", "freight", "cost", "tax", "vat", "total", "subtotal", "insurance", "charge", "fee", "доставка", "налог", "итого"]

            for item in all_items:
                # Handle key variations
                designation = (item.get("designation") or item.get("part_no") or "").replace(" ", "")
                material = item.get("material") or item.get("material_on_drawing") or item.get("material_on_quotation")
                description = item.get("description") or item.get("remark") or ""
                name = item.get("name") or ""
                
                # Heuristic: Swap Designation and Name if Designation looks like a Name (Cyrillic) and Name is empty
                if designation and not name:
                    if re.search('[а-яА-Я]', designation):
                        name = designation
                        designation = ""

                # FILTERING LOGIC
                check_str = (designation + " " + name + " " + description).lower()
                if any(kw in check_str for kw in EXCLUDE_KEYWORDS):
                    continue
                
                items.append({
                    "designation": designation,
                    "raw_description": description,
                    "material": material,
                    "name": name,
                    "quantity": item.get("quantity") or 1,
                    "weight": 0.0,
                    "dimensions": "",
                    "description": "",
                    "parsing_method": f"DeepSeek ({model_slug})"
                })
            
            print(f"DeepSeek found {len(items)} items total.", flush=True)
            debug_info["method_used"] = "DeepSeek"

            # Deduplication Logic
            unique_items = []
            seen_hashes = set()
            
            for item in items:
                des = (item.get("designation") or "").strip().lower()
                mat = (item.get("material") or "").strip().lower()
                
                if not des:
                    item_hash = f"{item.get('raw_description')}|{mat}"
                else:
                    item_hash = f"{des}|{mat}"
                
                if item_hash in seen_hashes:
                    continue
                
                seen_hashes.add(item_hash)
                unique_items.append(item)
            
            items = unique_items


        except Exception as e:
            print(f"Error parsing with DeepSeek: {e}")
            debug_info["error"] = str(e)
    # Image Lookup Logic
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # In Docker, images are mounted to /app/images
    IMAGES_DIR = os.path.join(BASE_DIR, "images")
    
    if os.path.exists(IMAGES_DIR):
        print(f"Scanning for images in {IMAGES_DIR}...")
        image_files = os.listdir(IMAGES_DIR)
        
        for item in items:
            designation = item.get("designation")
            if not designation: continue
            
            # Try exact match with common extensions
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                candidate_name = f"{designation}{ext}"
                if candidate_name in image_files:
                    item["image_path"] = candidate_name
                    break
            
            if item.get("image_path"):
                continue
                
            # Try match without suffix (e.g. R1.01.00.001a -> R1.01.00.001.jpg)
            if designation[-1].isalpha():
                base_des = designation[:-1]
                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    candidate_name = f"{base_des}{ext}"
                    if candidate_name in image_files:
                        item["image_path"] = candidate_name
                        break
            
            if item.get("image_path"):
                continue
            
            # Try to find any file that STARTS with the designation
            for img_file in image_files:
                if img_file.startswith(designation) and img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    item["image_path"] = img_file
                    break

    return items, debug_info
