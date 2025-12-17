import os
from PIL import Image
import uuid

# Define constants
MAX_IMAGE_DIMENSION = 1024
IMAGE_QUALITY = 80
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "images")

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

def process_and_save_image(pil_image: Image.Image) -> str:
    """
    Resizes image if too large, converts to WebP, saves to disk, and returns the filename.
    """
    # Resize if needed
    width, height = pil_image.size
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        ratio = min(MAX_IMAGE_DIMENSION / width, MAX_IMAGE_DIMENSION / height)
        new_size = (int(width * ratio), int(height * ratio))
        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Generate filename
    filename = f"{uuid.uuid4()}.webp"
    filepath = os.path.join(IMAGES_DIR, filename)
    
    # Save as WebP
    pil_image.save(filepath, "WEBP", quality=IMAGE_QUALITY)
    
    return filename

def get_image_path(filename: str) -> str:
    """Returns absolute path for a given filename"""
    return os.path.join(IMAGES_DIR, filename)
