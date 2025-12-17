from docx import Document
import zipfile
import os

docx_path = "_для бд/Техническое описание по 2023668805.docx"
extract_dir = "temp_docx_new_data"

try:
    # Text inspection
    doc = Document(docx_path)
    print("--- DOCX TEXT PREVIEW (First 20 paras) ---")
    for i, p in enumerate(doc.paragraphs[:20]):
        if p.text.strip():
            print(f"{i}: {p.text.strip()}")
            
    # Image inspection
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
        
    print("\n--- IMAGES FOUND ---")
    media_dir = os.path.join(extract_dir, "word", "media")
    if os.path.exists(media_dir):
        for f in os.listdir(media_dir):
            print(f)
    else:
        print("No media folder found.")
        
except Exception as e:
    print(f"Error: {e}")
