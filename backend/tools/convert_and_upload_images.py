"""
Скрипт для конвертации JFIF изображений в WebP и загрузки в MinIO
"""
import os
import sys
from PIL import Image
import boto3
from io import BytesIO

# Настройки
IMAGES_DIR = r"d:\Work\_develop\_gen_for_ tamozh\_dev\_изображения"
MAX_DIMENSION = 1024
QUALITY = 80

# MinIO/S3 настройки (из .env или напрямую)
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "tamozh-images")

# JFIF файлы для конвертации
JFIF_FILES = [
    "ASDB2PW0001.jfif",
    "ASDB2EN0001.jfif",
    "ECMAC20604RS.jfif",
    "6ES7 212-1AE40-0XB0.jfif",
    "6ES7 221-3AD30-0XB0.jfif",
    "6ES7 231-5QD32-0XB0.jfif",
    "TFT- 6AV2 123-2DB03-0AX0.jfif",
    "asd-b2-0421b-b.jfif"
]

def convert_to_webp(input_path, output_path):
    """Конвертирует изображение в WebP с ресайзом"""
    with Image.open(input_path) as img:
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Ресайз если слишком большое
        width, height = img.size
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            ratio = min(MAX_DIMENSION / width, MAX_DIMENSION / height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"  Resized: {width}x{height} -> {new_size[0]}x{new_size[1]}")
        
        # Сохраняем как WebP
        img.save(output_path, "WEBP", quality=QUALITY)
        print(f"  Saved: {output_path}")
        return True
    return False

def upload_to_minio(file_path, object_name):
    """Загружает файл в MinIO"""
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )
        
        with open(file_path, 'rb') as f:
            s3_client.upload_fileobj(
                f,
                S3_BUCKET_NAME,
                object_name,
                ExtraArgs={'ContentType': 'image/webp'}
            )
        print(f"  Uploaded to MinIO: {object_name}")
        return True
    except Exception as e:
        print(f"  ERROR uploading to MinIO: {e}")
        return False

def main():
    print("=" * 50)
    print("JFIF -> WebP Converter & MinIO Uploader")
    print("=" * 50)
    
    converted = 0
    uploaded = 0
    
    for jfif_file in JFIF_FILES:
        input_path = os.path.join(IMAGES_DIR, jfif_file)
        
        if not os.path.exists(input_path):
            print(f"\n[SKIP] Not found: {jfif_file}")
            continue
        
        # Имя WebP файла
        webp_name = os.path.splitext(jfif_file)[0] + ".webp"
        output_path = os.path.join(IMAGES_DIR, webp_name)
        
        print(f"\n[CONVERT] {jfif_file}")
        
        # Конвертация
        if convert_to_webp(input_path, output_path):
            converted += 1
            
            # Загрузка в MinIO
            if upload_to_minio(output_path, webp_name):
                uploaded += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {converted} converted, {uploaded} uploaded")
    print("=" * 50)

if __name__ == "__main__":
    main()
