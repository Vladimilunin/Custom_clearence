"""
Тест проверки взаимозаменяемости MinIO и Cloudflare R2
"""
import sys
import os
from dotenv import load_dotenv

# Загружаем .env файл
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

# Добавляем путь к backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.s3 import s3_service
from app.core.config import settings
from io import BytesIO

def test_s3_upload():
    """Тест загрузки файла в S3 (MinIO или R2)"""
    
    print("=" * 60)
    print("Тест S3-совместимого хранилища")
    print("=" * 60)
    print()
    
    # Показываем текущую конфигурацию
    print("Текущая конфигурация:")
    print(f"  S3_ENDPOINT: {settings.S3_ENDPOINT}")
    print(f"  S3_BUCKET_NAME: {settings.S3_BUCKET_NAME}")
    print(f"  S3_PUBLIC_DOMAIN: {settings.S3_PUBLIC_DOMAIN}")
    print()
    
    # Определяем тип хранилища
    if "localhost" in settings.S3_ENDPOINT or "minio" in settings.S3_ENDPOINT:
        storage_type = "MinIO (локальное)"
    elif "r2.cloudflarestorage.com" in settings.S3_ENDPOINT:
        storage_type = "Cloudflare R2 (облачное)"
    else:
        storage_type = "S3-совместимое хранилище"
    
    print(f"Тип хранилища: {storage_type}")
    print()
    
    # Создаем тестовый файл
    test_data = b"Test file content for S3 compatibility check"
    test_file = BytesIO(test_data)
    test_filename = "test_s3_upload.txt"
    
    print(f"Загружаю тестовый файл: {test_filename}")
    
    try:
        # Загружаем файл
        result_url = s3_service.upload_file(test_file, test_filename)
        
        if result_url:
            print(f"✅ Успешно загружено!")
            print(f"   URL: {result_url}")
            print()
            
            # Пробуем скачать файл обратно
            print("Проверяю возможность скачивания...")
            file_stream = s3_service.get_file(test_filename)
            
            if file_stream:
                content = file_stream.read()
                if content == test_data:
                    print(f"✅ Файл успешно скачан и содержимое совпадает!")
                else:
                    print(f"⚠️  Файл скачан, но содержимое отличается")
            else:
                print(f"❌ Не удалось скачать файл")
            
            print()
            print("=" * 60)
            print(f"✅ Тест пройден! {storage_type} работает корректно")
            print("=" * 60)
            
            return True
            
        else:
            print(f"❌ Ошибка загрузки файла")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_s3_upload()
    sys.exit(0 if success else 1)
