import os
import sys
import json
import requests
import base64
from io import BytesIO
import pypdfium2 as pdfium
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

def analyze_pdf(pdf_path):
    print(f"Analyzing PDF: {pdf_path}")
    
    # Convert PDF to images
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        print(f"Rendered {len(pdf)} pages.")
    except Exception as e:
        print(f"Error rendering PDF: {e}")
        return

    # Use Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY not found!")
        return

    model = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    # Analyze first page only for structure
    page = pdf[0]
    bitmap = page.render(scale=2) # Render at higher resolution
    pil_image = bitmap.to_pil()
    
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    prompt = """Analyze this invoice/document page. 
    1. Identify all distinct columns in the main table.
    2. Identify all header fields (metadata) such as Invoice No, Date, Buyer, Seller, Payment Terms, etc.
    3. Return a JSON object listing the 'columns' found and 'metadata_fields' found.
    4. Also extract the first 3 rows of the table as 'sample_rows' to see data types.
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                ]
            }
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            print("Analysis Result:")
            print(content)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    pdf_path = r"d:\Work\_develop\_gen_for_ tamozh\_dev\BETTERONE-ISA25112201\4_PI For Алексей Семенов- 20241225.pdf"
    analyze_pdf(pdf_path)
