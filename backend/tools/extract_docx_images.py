import os
import zipfile
import re
import shutil
from docx import Document

docx_path = "_для бд/Техническое описание по 2023668805.docx"
output_dir = "_изображения"
temp_dir = "temp_docx_extract_images"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

try:
    # 1. Extract all images first
    print(f"Extracting images from {docx_path}...")
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    media_dir = os.path.join(temp_dir, "word", "media")
    if not os.path.exists(media_dir):
        print("No media directory found in DOCX.")
        exit()

    # Map internal image names (image1.png) to their order in the document
    # This is tricky. The order in /word/media is not guaranteed to be the display order.
    # However, usually image1.png is the first one added.
    # A better way is to parse document.xml, but for now let's try to correlate 
    # "Фото (эскиз) X" with imageX.ext if the numbering matches.
    # OR, we can iterate through the document, find the "Фото..." text, and assume the NEXT image is the one.
    # But python-docx doesn't easily give us the image filename for a shape.
    
    # Let's look at the relationships.
    # But for a quick script, let's assume the images in media folder are roughly in order 
    # OR we can try to match "imageN" with "Position N".
    # Let's look at the text first.
    
    doc = Document(docx_path)
    
    image_map = {} # Index -> Description
    
    current_pos = 0
    for p in doc.paragraphs:
        text = p.text.strip()
        # Match "Фото (эскиз) 1.  Фитинг гидравлический BFC-01-01"
        match = re.search(r"Фото \(эскиз\) (\d+)\.\s*(.*)", text)
        if match:
            idx = int(match.group(1))
            desc = match.group(2).strip()
            # Clean description for filename
            safe_desc = re.sub(r'[\\/*?:"<>|]', "", desc)
            image_map[idx] = safe_desc
            print(f"Found description for image {idx}: {safe_desc}")

    # Now let's list the images. 
    # In many generated docs, image1 goes with Position 1, etc.
    # Let's try to match imageN with Position N.
    
    files = os.listdir(media_dir)
    # Sort files to ensure image1, image2, ... image10 order
    # Extract number from filename
    def get_num(fname):
        m = re.search(r"image(\d+)", fname)
        return int(m.group(1)) if m else 0
        
    sorted_files = sorted(files, key=get_num)
    
    print(f"Found {len(sorted_files)} images.")
    
    for fname in sorted_files:
        num = get_num(fname)
        if num in image_map:
            desc = image_map[num]
            ext = os.path.splitext(fname)[1]
            new_name = f"{desc}{ext}"
            src = os.path.join(media_dir, fname)
            dst = os.path.join(output_dir, new_name)
            
            # Avoid overwriting if exists, or maybe overwrite?
            shutil.copy(src, dst)
            print(f"Saved: {fname} -> {new_name}")
        else:
            print(f"Skipping {fname} (No matching description for index {num})")

except Exception as e:
    print(f"Error: {e}")
finally:
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
