import pypdfium2 as pdfium
import pytesseract
import requests
import os

pdf_path = "../_примеры инвойсов/FL202510240002.pdf"
filename = os.path.basename(pdf_path)

print(f"Testing OCR methods on: {pdf_path}")
print("="*50)

# 1. Test Local Tesseract
print("\n--- 1. Testing Local Tesseract ---")
try:
    ocr_text_local = ""
    pdf_doc = pdfium.PdfDocument(pdf_path)
    for i in range(len(pdf_doc)):
        page = pdf_doc.get_page(i)
        bitmap = page.render(scale=2)
        pil_image = bitmap.to_pil()
        page_text = pytesseract.image_to_string(pil_image, lang='eng+rus')
        ocr_text_local += page_text + "\n"
    
    print("SUCCESS. Extracted text snippet:")
    print("-" * 20)
    print(ocr_text_local[:300])
    print("-" * 20)
except Exception as e:
    print(f"FAILED: {e}")

# 2. Test Cloud OCR (OCR.space)
print("\n--- 2. Testing Cloud OCR (OCR.space) ---")
try:
    payload = {
        'apikey': 'helloworld', # Demo key
        'language': 'eng',
        'isOverlayRequired': False
    }
    with open(pdf_path, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
        )
    
    result = r.json()
    if result.get('IsErroredOnProcessing'):
        print(f"FAILED: {result.get('ErrorMessage')}")
    else:
        ocr_text_cloud = ""
        for parsed_result in result.get('ParsedResults', []):
            ocr_text_cloud += parsed_result.get('ParsedText', "") + "\n"
            
        print("SUCCESS. Extracted text snippet:")
        print("-" * 20)
        print(ocr_text_cloud)
        print("-" * 20)

except Exception as e:
    print(f"FAILED: {e}")
