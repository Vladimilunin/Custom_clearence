import pypdfium2 as pdfium
import re
import os

file_path = "../_примеры инвойсов/FL202510240002.pdf"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    try:
        pdf = pdfium.PdfDocument(file_path)
        text = ""
        for i in range(len(pdf)):
            page = pdf.get_page(i)
            textpage = page.get_textpage()
            text += textpage.get_text_range() + "\n"
            
        print("--- EXTRACTED TEXT (pypdfium2) ---")
        print(text)
        print("----------------------")
    except Exception as e:
        print(f"Error with pypdfium2: {e}")
    
    # Test current regex
    # Current regex in parser.py (approximate, I need to check the file to be sure, but I'll use a generic one for testing)
    # Assuming it's looking for R1...
    
    lines = text.split('\n')
    for line in lines:
        if "R1" in line:
            print(f"Line with R1: {line}")
            # Try to extract material
            # Regex from parser.py (I'll read it in a moment, but let's try to guess/prototype)
            # Expected: "Material: Inconel 625" or similar?
