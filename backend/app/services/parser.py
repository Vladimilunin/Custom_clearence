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
        debug_info["page_count"] = len(images)
    except Exception as e:
        print(f"Rendering failed: {e}")
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
    base64_images = []
    for img in images:
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        base64_images.append(img_str)

    print(f"DEBUG: Prepared {len(base64_images)} images for Groq.")

    all_items = []
    invoice_metadata = {}
    key_attempts_log = []

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
        page_success = False

        # Try models
        for model_slug in GROQ_MODELS:
            if page_success:
                break

            print(f"--- Page {i+1}: Trying model {model_slug} ---")

            # Try keys
            for key_idx, current_api_key in enumerate(GROQ_API_KEYS):
                if page_success:
                    break

                print(f"--- Page {i+1}: Trying Key {key_idx+1}/{len(GROQ_API_KEYS)} ({current_api_key[-4:]}) ---")

                headers = {
                    "Authorization": f"Bearer {current_api_key}",
                    "Content-Type": "application/json"
                }

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
                        content_str = resp_json['choices'][0]['message']['content']

                        # Clean JSON
                        if "```json" in content_str:
                            content_str = content_str.split("```json")[1].split("```")[0]
                        elif "```" in content_str:
                            content_str = content_str.split("```")[1].split("```")[0]

                        print(f"DEBUG: Raw JSON from Groq (Page {i+1}): {content_str[:100]}...")

                        data = json.loads(content_str)

                        # Aggregate items
                        page_items = data.get("items", [])
                        if isinstance(page_items, list):
                            all_items.extend(page_items)

                        # Aggregate metadata (only from first page)
                        if i == 0:
                            invoice_metadata["invoice_number"] = data.get("invoice_number")
                            invoice_metadata["invoice_date"] = normalize_date(data.get("invoice_date"))
                            invoice_metadata["contract_number"] = data.get("contract_number")
                            invoice_metadata["contract_date"] = normalize_date(data.get("contract_date"))
                            invoice_metadata["supplier"] = data.get("supplier")

                        page_success = True
                        key_attempts_log.append({
                            "page": i+1,
                            "status": "success",
                            "key_idx": key_idx,
                            "model": model_slug,
                            "tokens": resp_json.get('usage', {}).get('total_tokens', 0)
                        })
                        print(f"✅ Page {i+1} Success with Key {key_idx+1}")

                    else:
                        error_msg = response.text
                        status_code = response.status_code
                        print(f"❌ Page {i+1} Failed with Key {key_idx+1}: {status_code} - {error_msg[:100]}")

                        key_attempts_log.append({
                            "page": i+1,
                            "status": "failed",
                            "key_idx": key_idx,
                            "model": model_slug,
                            "error": f"{status_code}: {error_msg[:50]}"
                        })

                        # Retry only on specific errors
                        if status_code in [401, 429, 500, 503]:
                            continue  # Try next key
                        else:
                            break  # Try next model

                except Exception as e:
                    print(f"❌ Page {i+1} Exception with Key {key_idx+1}: {e}")
                    key_attempts_log.append({
                        "page": i+1,
                        "status": "error",
                        "key_idx": key_idx,
                        "model": model_slug,
                        "error": str(e)[:50]
                    })
                    continue  # Try next key

        if not page_success:
            print(f"💀 Page {i+1} failed with ALL keys and ALL models.")
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
