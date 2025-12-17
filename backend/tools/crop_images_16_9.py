import sys
import os
from PIL import Image

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

images_dir = "_изображения"

# List of files to process (based on previous step's output)
target_files = [
    "BFC-01-01.jpg", 
    "ME-01-02.jpg", 
    "T-02.jpg", 
    "R11.jpg", 
    "MC-01-01.jpg", 
    "RVH-01.jpg", 
    "BV3W-01.jpg", 
    "UT-01.jpg", 
    "Plug-01.jpg", 
    "MBT-01.jpg", 
    "BU-01-0.jpg", 
    "BF+FF-01.jpg"
]

def crop_to_16_9(img):
    width, height = img.size
    target_ratio = 16 / 9
    current_ratio = width / height
    
    if current_ratio > target_ratio:
        # Too wide, crop width
        new_width = int(height * target_ratio)
        offset = (width - new_width) // 2
        return img.crop((offset, 0, offset + new_width, height))
    elif current_ratio < target_ratio:
        # Too tall, crop height
        new_height = int(width / target_ratio)
        offset = (height - new_height) // 2
        return img.crop((0, offset, width, offset + new_height))
    else:
        return img

def process_images():
    print("Processing images for 16:9 crop...")
    
    count = 0
    for filename in target_files:
        path = os.path.join(images_dir, filename)
        if os.path.exists(path):
            try:
                print(f"Processing {filename}...")
                img = Image.open(path)
                cropped_img = crop_to_16_9(img)
                cropped_img.save(path)
                count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        else:
            print(f"File not found: {filename}")
            
    print(f"Finished. Cropped {count} images.")

if __name__ == "__main__":
    process_images()
