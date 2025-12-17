import pandas as pd
from sqlalchemy.orm import Session
from app.db.models import Part
import os

def clean_float(value):
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Replace comma with dot and remove non-numeric characters except dot
        clean_val = value.replace(',', '.').strip()
        try:
            return float(clean_val)
        except ValueError:
            return None
    return None

def clean_str(value):
    if pd.isna(value):
        return None
    return str(value).strip()

def import_parts_from_excel(file_path: str, db: Session):
    # Image mapping logic
    image_map = {}
    # In Docker, images are mounted to /app/images
    # Fallback to local dev path if needed
    if os.path.exists("/app/images"):
        image_dir = "/app/images"
    else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Try backend/images
        image_dir = os.path.join(BASE_DIR, "images")
        if not os.path.exists(image_dir) or not os.listdir(image_dir):
             # Try project root _изображения
             image_dir = os.path.abspath(os.path.join(BASE_DIR, "../_изображения"))

    def normalize_name(name):
        return "".join(c.lower() for c in name if c.isalnum())

    if os.path.exists(image_dir):
        print(f"Scanning images in {image_dir}...")
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                name_part = os.path.splitext(filename)[0]
                ext = os.path.splitext(filename)[1].lower()
                
                # Exact match logic
                # Prioritize WebP
                current_val = image_map.get(name_part)
                if current_val:
                    current_ext = os.path.splitext(current_val)[1].lower()
                    if current_ext != '.webp' and ext == '.webp':
                        image_map[name_part] = filename
                else:
                    image_map[name_part] = filename

                # Also try to map just the designation part if it has extra text
                parts = name_part.split(' ')
                if parts:
                    des = parts[0]
                    current_val_des = image_map.get(des)
                    if current_val_des:
                        current_ext_des = os.path.splitext(current_val_des)[1].lower()
                        if current_ext_des != '.webp' and ext == '.webp':
                            image_map[des] = filename
                    else:
                        image_map[des] = filename
                        
                # Fuzzy match map (normalized -> filename)
                norm_name = normalize_name(name_part)
                if norm_name not in image_map: # Don't overwrite exact matches
                     image_map[norm_name] = filename
    else:
        print(f"Image directory not found: {image_dir}")

    print(f"Reading Excel file: {file_path}")
    try:
        # Try xlrd first as it is .xls
        df = pd.read_excel(file_path, engine='xlrd', header=None)
    except Exception:
        try:
            df = pd.read_excel(file_path, engine='openpyxl', header=None)
        except Exception as e:
            print(f"Failed to read excel: {e}")
            return

    # Find header row
    header_row_index = -1
    column_map = {}
    
    # Common column names mapping to internal keys
    # Internal keys: 'Обозначение', 'Наименование', 'Материал', 'Масса', 'Размеры', 'Спецификация', 'Раздел'
    possible_headers = {
        'Обозначение': 'Обозначение',
        'Model': 'Обозначение',
        'Part No.': 'Обозначение',
        'Наименование': 'Наименование',
        'Product Name': 'Наименование',
        'Description': 'Спецификация', # Or Description -> Спецификация
        'Материал': 'Материал',
        'Material': 'Материал',
        'Масса': 'Масса',
        'Weight': 'Масса',
        'Размеры': 'Размеры',
        'Размер': 'Размеры',
        'Габариты': 'Размеры',
        'Габаритные размеры': 'Размеры',
        'Dimensions': 'Размеры',
        'Спецификация': 'Спецификация',
        'Раздел': 'Раздел',
        'Вес': 'Масса',
        'Масса единицы, кг': 'Масса'
    }

    for i, row in df.iterrows():
        # Convert row to string values for checking
        row_values = [str(val).strip() for val in row.values]
        
        # Check if this row contains enough known headers
        matches = 0
        temp_map = {}
        for col_idx, val in enumerate(row_values):
            if val in possible_headers:
                matches += 1
                temp_map[possible_headers[val]] = col_idx
        
        if matches >= 2: # At least 2 columns match
            header_row_index = i
            column_map = temp_map
            print(f"Found header at row {i}: {column_map}")
            break
    
    if header_row_index == -1:
        print("Could not find header row.")
        return

    # Iterate from the next row
    count = 0
    for index in range(header_row_index + 1, len(df)):
        row = df.iloc[index]
        
        # Helper to get value by mapped column index
        def get_val(key):
            if key in column_map:
                return row[column_map[key]]
            return None

        designation = get_val('Обозначение')
        if pd.isna(designation) or str(designation).strip() == '' or str(designation).lower() == 'nan':
            continue
            
        # Normalize spaces (collapse multiple spaces)
        designation = " ".join(str(designation).strip().replace('\xa0', ' ').split())
        
        # Split designation if it contains spaces (e.g. "R1.301 Пластина" -> "R1.301")
        # But keep the original for image lookup if needed
        original_designation = designation
        if ' ' in designation:
            clean_designation = designation.split(' ')[0]
            # Heuristic: if the first part looks like a code (alphanumeric), use it
            if len(clean_designation) > 1:
                designation = clean_designation
                print(f"Using cleaned designation: {original_designation} -> {designation}")

        if 'R1.301' in designation:
            print(f"Processing R1.301: {repr(designation)} (Original: {repr(original_designation)})")
            
            if original_designation in image_map:
                print(f"  Found full name in image_map: {image_map[original_designation]}")
            if designation in image_map:
                 print(f"  Found cleaned name in image_map: {image_map[designation]}")
        
        try:
            # Check if exists
            existing = db.query(Part).filter(Part.designation == designation).first()
            
            # If not found, try splitting by space (e.g. "R1.301 Name" -> "R1.301")
            if not existing and ' ' in designation:
                clean_designation = designation.split(' ')[0]
                existing = db.query(Part).filter(Part.designation == clean_designation).first()
                if existing:
                    print(f"Found existing part by cleaned designation: {designation} -> {clean_designation}")
                    designation = clean_designation
            
            name = clean_str(get_val('Наименование'))
            material = clean_str(get_val('Материал'))
            
            # Handle multiple possible column names for Weight
            weight = clean_float(get_val('Масса'))
                
            # Handle multiple possible column names for Dimensions
            dimensions = clean_str(get_val('Размеры'))
                
            description = clean_str(get_val('Спецификация'))
            section = clean_str(get_val('Раздел'))
            
            # Find image
            image_filename = image_map.get(designation)
            
            # If not exact match, try fuzzy match
            if not image_filename:
                norm_des = normalize_name(designation)
                image_filename = image_map.get(norm_des)
            
            # Try splitting by space for image lookup (e.g. "R1.301 Name" -> "R1.301")
            if not image_filename and ' ' in designation:
                 clean_des = designation.split(' ')[0]
                 image_filename = image_map.get(clean_des)
                 if image_filename:
                     print(f"Found image for cleaned designation: {designation} -> {clean_des}")
                     designation = clean_des

            # If still not found, try prefix match
            if not image_filename:
                 for key, val in image_map.items():
                     if key.startswith(designation):
                         image_filename = val
                         break
            
            if not image_filename:
                print(f"Skipping {designation}: No image found.")
                continue

            image_path = image_filename # Store just filename, we know the base dir
            
            if existing:
                # Update
                existing.name = name
                existing.material = material
                existing.weight = weight
                existing.dimensions = dimensions
                existing.description = description
                existing.section = section
                if image_path:
                    existing.image_path = image_path
            else:
                part = Part(
                    designation=designation,
                    name=name,
                    material=material,
                    weight=weight,
                    dimensions=dimensions,
                    description=description,
                    section=section,
                    image_path=image_path
                )
                db.add(part)
            
            count += 1
            if count % 50 == 0:
                db.commit()
                
        except Exception as e:
            print(f"Error on row {index} (Designation: {designation}): {e}")
            db.rollback()
            continue
    
    db.commit()
    print(f"Imported/Updated {count} parts.")
