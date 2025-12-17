# Переключение между MinIO и Cloudflare R2

## Обзор

Backend использует универсальный `S3Service` который работает с любым S3-совместимым хранилищем:
- **Локально:** MinIO
- **Облако:** Cloudflare R2

Оба используют один и тот же код через `boto3` библиотеку.

## Код S3 сервиса

[`backend/app/services/s3.py`](file:///d:/Work/_develop/_gen_for_%20tamozh/_dev/backend/app/services/s3.py):

```python
class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,      # MinIO или R2
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME
```

**Ключевой момент:** Один код работает с обоими хранилищами через изменение `S3_ENDPOINT`.

## Конфигурации

### Локальное (MinIO)

**Файл:** `backend/.env`

```env
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=tamozh-images
S3_PUBLIC_DOMAIN=http://localhost:9000
```

### Облачное (Cloudflare R2)

**Файл:** `backend/.env.cloud`

```env
S3_ENDPOINT=https://a3e756743a64a62e93a9b990fde76041.r2.cloudflarestorage.com
S3_ACCESS_KEY=ca510f34035fb42d3c995997d5c681f4
S3_SECRET_KEY=d413607932eb1e783befdf6903005db979e0c2904ba37e239d0bd57e34518b7a
S3_BUCKET_NAME=customs-images
S3_PUBLIC_DOMAIN=https://pub-a3e756743a64a62e93a9b990fde76041.r2.dev
```

## Переключение между хранилищами

### Вариант 1: Через разные .env файлы

**Для локальной разработки:**
```bash
cp backend/.env.local backend/.env
docker-compose restart backend
```

**Для тестирования с R2:**
```bash
cp backend/.env.cloud backend/.env
docker-compose restart backend
```

### Вариант 2: Docker compose override

Используйте разные docker-compose файлы:

**Локально:**
```bash
docker-compose up -d
```

**С R2 (облачное хранилище, локальная БД):**
```yaml
# docker-compose.override.yml
services:
  backend:
    environment:
      - S3_ENDPOINT=https://...r2.cloudflarestorage.com
      - S3_ACCESS_KEY=your_key
      - S3_SECRET_KEY=your_secret
      - S3_BUCKET_NAME=customs-images
```

### Вариант 3: Environment variables

```bash
docker-compose exec backend env S3_ENDPOINT=https://...r2.cloudflarestorage.com python test.py
```

## Тестирование совместимости

Создан тестовый скрипт: [`test_s3_compatibility.py`](file:///d:/Work/_develop/_gen_for_%20tamozh/_dev/test_s3_compatibility.py)

**Запуск:**

```bash
# Тест с MinIO (локально)
python test_s3_compatibility.py

# Тест с R2 (нужно переключить .env)
cp backend/.env.cloud backend/.env
python test_s3_compatibility.py
```

**Что проверяется:**
1. ✅ Загрузка файла
2. ✅ Получение файла обратно
3. ✅ Проверка содержимого
4. ✅ Автоопределение типа хранилища

## Функции S3Service

### upload_file(file_obj, object_name)

Загружает файл в хранилище.

**Параметры:**
- `file_obj` - file-like object (BytesIO, открытый файл)
- `object_name` - имя файла в bucket

**Возвращает:**
- Полный URL если настроен `S3_PUBLIC_DOMAIN`
- Имя файла если `S3_PUBLIC_DOMAIN` не настроен

**Пример:**
```python
from app.services.s3 import s3_service
from io import BytesIO

file = BytesIO(b"content")
url = s3_service.upload_file(file, "test.txt")
# MinIO: http://localhost:9000/tamozh-images/test.txt
# R2: https://pub-xxx.r2.dev/test.txt
```

### get_file(object_name)

Получает файл из хранилища.

**Параметры:**
- `object_name` - имя файла в bucket

**Возвращает:**
- Stream объект (Body from boto3)

**Пример:**
```python
stream = s3_service.get_file("test.txt")
content = stream.read()
```

## Миграция изображений из MinIO в R2

### Способ 1: MC (MinIO Client)

```bash
# Настроить aliases
mc alias set local http://localhost:9000 minioadmin minioadmin
mc alias set r2 https://...r2.cloudflarestorage.com ACCESS_KEY SECRET_KEY

# Скопировать все
mc mirror local/tamozh-images r2/customs-images
```

### Способ 2: AWS CLI с R2

```bash
# Установить AWS CLI
pip install awscli

# Скопировать из локальной папки в R2
aws s3 sync _изображения/ s3://customs-images/ \
  --endpoint-url https://...r2.cloudflarestorage.com \
  --profile r2
```

### Способ 3: Python скрипт

```python
import boto3
from io import BytesIO

# MinIO client
minio = boto3.client('s3', 
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin')

# R2 client
r2 = boto3.client('s3',
    endpoint_url='https://...r2.cloudflarestorage.com',
    aws_access_key_id='your_key',
    aws_secret_access_key='your_secret')

# Копировать все объекты
response = minio.list_objects_v2(Bucket='tamozh-images')
for obj in response.get('Contents', []):
    print(f"Copying {obj['Key']}...")
    
    # Скачать из MinIO
    file_obj = minio.get_object(Bucket='tamozh-images', Key=obj['Key'])
    content = file_obj['Body'].read()
    
    # Загрузить в R2
    r2.put_object(Bucket='customs-images', Key=obj['Key'], 
                  Body=BytesIO(content), ACL='public-read')
```

## Production Deployment

При деплое на Cloud Run:

1. **Backend использует R2** - настройки из `.env.cloud`
2. **Изображения доступны публично** через `https://pub-xxx.r2.dev/`
3. **Автоматическая загрузка** при парсинге инвойсов
4. **Генерация документов** подтягивает изображения из R2

## Проверка в production

После деплоя:

```bash
# Проверить endpoint
curl https://backend-service-xxx.run.app/

# Загрузить тестовый инвойс
curl -X POST https://backend-service-xxx.run.app/api/v1/invoices/upload \
  -F "file=@test.pdf"

# Проверить что изображение загружено в R2
curl https://pub-xxx.r2.dev/test_image.jpg
```

## Troubleshooting

### Проблема: 403 Forbidden при доступе к R2

**Решение:** Проверьте bucket policy и CORS:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::customs-images/*"
    }
  ]
}
```

### Проблема: MinIO connection refused

**Решение:** 
```bash
docker-compose ps minio  # Проверить что запущен
docker-compose logs minio  # Проверить логи
```

### Проблема: Изображения не отображаются

**Решение:** Проверьте `S3_PUBLIC_DOMAIN`:
- MinIO: `http://localhost:9000`
- R2: `https://pub-xxx.r2.dev` (из R2 settings)

## Итого

✅ **MinIO и R2 полностью взаимозаменяемы**  
✅ **Один код работает с обоими**  
✅ **Переключение через .env файлы**  
✅ **Миграция данных простая**  
✅ **Production использует R2**  
✅ **Development использует MinIO**  

Это обеспечивает гибкость разработки локально и надежность в production!
