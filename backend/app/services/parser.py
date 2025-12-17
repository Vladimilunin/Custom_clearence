"""
Invoice PDF Parser - Groq Multi-Key Implementation
Parses PDF invoices using Groq AI with key rotation and model fallback.
"""
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple

import pypdfium2 as pdfium
from PIL import Image

from app.core.config import settings


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

    # Pre-processing: remove "th", "st", "nd", "rd" suffixes after digits
    clean_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

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

    for fmt in formats:
        try:
            dt = datetime.strptime(clean_str, fmt)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue

    return date_str  # Return original if parsing fails


def _render_pages(pdf_path: str) -> List[Image.Image]:
    """Render all pages of a PDF to PIL images."""
    import pypdfium2 as pdfium
    
    images = []
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
        return images
    except Exception as e:
        print(f"Rendering failed: {e}")
        raise e


def _encode_image(image: Image.Image) -> str:
    """Encode PIL image to base64."""
    import base64
    from io import BytesIO
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


PAGE_PROMPT = """Extract all line items from this invoice page. Return a valid JSON object with this structure:
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


def _process_page(
    page_index: int, 
    b64_img: str, 
    models: List[str], 
    api_keys: List[str],
    max_retries: int = 3
) -> Tuple[List[Dict], Dict, List[Dict]]:
    """
    Process a single page with Groq AI using model/key rotation.
    
    Features:
    - Model fallback (tries multiple models)
    - Key rotation (tries multiple API keys)
    - Exponential backoff for rate limits
    
    Args:
        page_index: 0-based page index
        b64_img: Base64-encoded image
        models: List of model slugs to try
        api_keys: List of API keys to rotate
        max_retries: Max retries per key for transient errors
        
    Returns: (items, metadata, logs)
    """
    import requests
    import time
    
    items = []
    metadata = {}
    logs = []
    success = False

    for model_slug in models:
        if success:
            break
            
        print(f"--- Page {page_index+1}: Trying model {model_slug} ---")
        
        for key_idx, api_key in enumerate(api_keys):
            if success:
                break
                
            print(f"--- Page {page_index+1}: Trying Key {key_idx+1}/{len(api_keys)} ({api_key[-4:]}) ---")
            
            # Retry logic with exponential backoff
            for retry in range(max_retries):
                if success:
                    break
                    
                if retry > 0:
                    wait_time = 2 ** retry  # 2, 4, 8 seconds
                    print(f"⏳ Retry {retry}/{max_retries}, waiting {wait_time}s...")
                    time.sleep(wait_time)
            
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model_slug,
                    "messages": [{
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": PAGE_PROMPT},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ]
                    }],
                    "temperature": 0.1
                }
                
                try:
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(payload),
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        resp_json = response.json()
                        content = resp_json['choices'][0]['message']['content']
                        
                        # Basic cleanup
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0]
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0]
                        
                        print(f"DEBUG: Raw JSON from Groq (Page {page_index+1}): {content[:100]}...")
                        data = json.loads(content)
                        
                        if isinstance(data.get("items"), list):
                            items = data["items"]
                        
                        # Metadata only if valid
                        metadata = {
                            "invoice_number": data.get("invoice_number"),
                            "invoice_date": normalize_date(data.get("invoice_date")),
                            "contract_number": data.get("contract_number"),
                            "contract_date": normalize_date(data.get("contract_date")),
                            "supplier": data.get("supplier")
                        }

                        logs.append({
                            "page": page_index+1,
                            "status": "success",
                            "key_idx": key_idx,
                            "model": model_slug,
                            "tokens": resp_json.get('usage', {}).get('total_tokens', 0),
                            "retries": retry
                        })
                        print(f"✅ Page {page_index+1} Success with Key {key_idx+1} (retries: {retry})")
                        success = True
                        break  # Exit retry loop
                        
                    elif response.status_code == 429:
                        # Rate limit - retry with backoff
                        print(f"⚠️ Rate limit hit, will retry...")
                        logs.append({
                            "page": page_index+1,
                            "status": "rate_limit",
                            "key_idx": key_idx,
                            "model": model_slug,
                            "retry": retry
                        })
                        continue  # Continue retry loop
                        
                    elif response.status_code in [500, 502, 503, 504]:
                        # Server error - retry
                        print(f"⚠️ Server error {response.status_code}, will retry...")
                        continue
                        
                    else:
                        print(f"❌ Page {page_index+1} Failed: {response.status_code} - {response.text[:100]}")
                        logs.append({
                            "page": page_index+1,
                            "status": "failed",
                            "key_idx": key_idx,
                            "model": model_slug,
                            "error": f"{response.status_code}: {response.text[:50]}"
                        })
                        break  # Try next key (don't retry for auth errors etc)
                        
                except requests.exceptions.Timeout:
                    print(f"⏱️ Timeout on page {page_index+1}, retry {retry+1}/{max_retries}")
                    logs.append({
                        "page": page_index+1,
                        "status": "timeout",
                        "retry": retry
                    })
                    continue
                    
                except Exception as e:
                    print(f"❌ Page {page_index+1} Exception: {e}")
                    logs.append({
                       "page": page_index+1,
                       "status": "error",
                       "error": str(e)[:50]
                    })
                    break  # Don't retry on unknown errors

    if not success:
        print(f"💀 Page {page_index+1} failed with ALL keys and ALL models.")
        
    return items, metadata, logs


def parse_invoice(pdf_path: str, method: str = "groq", api_key: str = None) -> Tuple[List[Dict], Dict]:
    """
    Parses the PDF invoice using Groq AI.
    
    Args:
        pdf_path: Path to the PDF file
        method: Parsing method (only 'groq' supported)
        api_key: Optional API key override
        
    Returns:
        Tuple of (items list, debug info dict)
    """
    import base64
    from io import BytesIO

    import requests

    items = []
    print(f"Parsing PDF: {pdf_path} with method={method}")

    debug_info = {
        "method_used": "Groq Multi-Key",
        "token_usage": None,
        "error": None,
        "page_count": 0
    }

    # Render PDF pages to images
    try:
        images = _render_pages(pdf_path)
        debug_info["page_count"] = len(images)
    except Exception as e:
        debug_info["error"] = f"Rendering failed: {e}"
        return [], debug_info

    # Groq API Keys (with rotation)
    GROQ_API_KEYS = [
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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',
        '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'
    ]

    # Add env key if present and not in list
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY not in GROQ_API_KEYS:
        GROQ_API_KEYS.insert(0, settings.GROQ_API_KEY)

    # Models to try (Primary + Fallbacks)
    GROQ_MODELS = [
        "meta-llama/llama-4-scout-17b-16e-instruct",  # Primary
        "llama-3.3-70b-versatile",                     # Fallback 1
        "llama-3.2-90b-vision-preview"                 # Fallback 2
    ]

    # Encode images to base64
    base64_images = [_encode_image(img) for img in images]
    print(f"DEBUG: Prepared {len(base64_images)} images for Groq.")

    all_items = []
    invoice_metadata = {}
    key_attempts_log = []

    for i, b64_img in enumerate(base64_images):
        page_items, page_metadata, page_logs = _process_page(i, b64_img, GROQ_MODELS, GROQ_API_KEYS)
        
        if page_items:
            all_items.extend(page_items)
            
        key_attempts_log.extend(page_logs)
        
        # Capture metadata from the first page
        if i == 0 and page_metadata:
            invoice_metadata = page_metadata

        # Check for complete failure on this page
        if not any(log["status"] == "success" for log in page_logs):
             debug_info["error"] = f"Page {i+1} failed after trying all keys/models."

    # Process items
    for item in all_items:
        items.append({
            "designation": (item.get("designation") or "").replace(" ", ""),
            "raw_description": item.get("description") or "",
            "material": item.get("material") or "",
            "name": item.get("name") or "",
            "quantity": item.get("quantity") or 1,
            "weight": 0.0,
            "dimensions": "",
            "description": "",
            "parsing_method": "Groq Multi-Key"
        })

    # Calculate total token usage
    total_tokens = sum(attempt.get("tokens", 0) for attempt in key_attempts_log if attempt.get("status") == "success")

    debug_info["invoice_metadata"] = invoice_metadata
    debug_info["key_attempts"] = key_attempts_log
    debug_info["token_usage"] = {
        "total_tokens": total_tokens,
        "prompt_tokens": 0,
        "completion_tokens": 0
    }
    print(f"Groq found {len(items)} items total. Total tokens: {total_tokens}")

    # Image standardization logic
    from app.services.image_processor import process_and_save_image

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    IMAGES_DIR = os.path.join(BASE_DIR, "images")

    if os.path.exists(IMAGES_DIR):
        print(f"Scanning for images in {IMAGES_DIR}...")
        image_files = os.listdir(IMAGES_DIR)

        for item in items:
            designation = item.get("designation")
            if not designation:
                continue

            found_image = None

            # Try exact match with common extensions
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                candidate_name = f"{designation}{ext}"
                if candidate_name in image_files:
                    found_image = candidate_name
                    break

            if not found_image:
                # Try match without suffix (e.g. R1.01.00.001a -> R1.01.00.001.jpg)
                if designation[-1].isalpha():
                    base_des = designation[:-1]
                    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                        candidate_name = f"{base_des}{ext}"
                        if candidate_name in image_files:
                            found_image = candidate_name
                            break

            if not found_image:
                # Try to find any file that STARTS with the designation
                for img_file in image_files:
                    if img_file.startswith(designation) and img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        found_image = img_file
                        break

            if found_image:
                try:
                    full_path = os.path.join(IMAGES_DIR, found_image)
                    with Image.open(full_path) as img:
                        if found_image.endswith(".webp"):
                            item["image_path"] = found_image
                        else:
                            # Convert to WebP and resize
                            new_filename = process_and_save_image(img)
                            item["image_path"] = new_filename
                            print(f"Converted {found_image} to {new_filename}")
                except Exception as e:
                    print(f"Error processing image {found_image}: {e}")
                    item["image_path"] = found_image

    return items, debug_info
