# Backend - Tamozh Document Generator API

FastAPI backend для генерации таможенных документов.

## Установка

### Локальная разработка

1. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env
   ```

4. **Примените миграции БД:**
   ```bash
   alembic upgrade head
   ```

5. **Запустите сервер:**
   ```bash
   uvicorn app.main:app --reload
   ```

API будет доступно по адресу: http://localhost:8000  
Документация: http://localhost:8000/docs

## Структура проекта

```
app/
├── api/              # API endpoints
│   └── api_v1/
│       ├── api.py    # Основной роутер
│       └── endpoints/
│           ├── invoices.py  # Загрузка и генерация
│           └── parts.py     # CRUD для деталей
├── core/             # Конфигурация
│   └── config.py     # Settings
├── db/               # База данных
│   ├── base.py       # Base model
│   ├── models.py     # SQLAlchemy модели
│   └── session.py    # DB session
├── services/         # Бизнес-логика
│   ├── generator.py  # Генерация DOCX
│   ├── parser.py     # AI парсинг PDF
│   ├── importer.py   # Импорт данных
│   └── s3.py         # S3/R2 operations
└── main.py           # FastAPI приложение

alembic/              # Миграции БД
├── versions/         # Файлы миграций
└── env.py            # Alembic конфигурация

scripts/              # Утилиты и тесты
```

## API Endpoints

### Invoices

**POST `/api/v1/invoices/upload`**
- Загрузка PDF инвойса и парсинг с помощью AI
- Parameters:
  - `file` (multipart/form-data): PDF файл
  - `method` (string): Метод парсинга (`auto`, `openrouter_gemini_2_5_flash_lite`, `siliconflow_qwen`, `deepseek_v3`)
  - `api_key` (string, optional): API ключ для AI
- Returns: Список распознанных товаров

**POST `/api/v1/invoices/generate`**
- Генерация таможенных документов
- Body (JSON):
  ```json
  {
    \"items\": [...],
    \"country_of_origin\": \"Китай\",
    \"contract_no\": \"...\",
    \"contract_date\": \"...\",
    \"supplier\": \"...\",
    \"gen_tech_desc\": true,
    \"gen_non_insurance\": false,
    \"gen_decision_130\": false,
    \"add_facsimile\": false
  }
  ```
- Returns: DOCX файл или ZIP архив

### Parts

**GET `/api/v1/parts`**
- Получение списка деталей
- Query params:
  - `skip` (int): Offset для пагинации
  - `limit` (int): Количество записей
  - `search` (string, optional): Поиск по обозначению/названию

**POST `/api/v1/parts`**
- Создание или обновление детали
- Body (JSON):
  ```json
  {
    \"designation\": \"...\",
    \"name\": \"...\",
    \"material\": \"...\",
    \"weight\": 0.0,
    \"dimensions\": \"...\",
    \"description\": \"...\"
  }
  ```

**PUT `/api/v1/parts/{part_id}`**
- Обновление существующей детали

## Модели данных

### Part (Деталь)

```python
class Part:
    id: int
    designation: str      # Обозначение (уникальное)
    name: str            # Наименование
    material: str        # Материал
    weight: float        # Масса
    dimensions: str      # Размеры
    description: str     # Описание/спецификация
    section: str         # Раздел
    image_path: str      # Путь к изображению
```

## Services

### Generator Service
Генерация DOCX документов:
- Техническое описание
- Письмо о нестраховании  
- Уведомление по Решению 130

Модули:
- `generate_technical_description()`
- `generate_non_insurance_letter()`
- `generate_decision_130_notification()`

### Parser Service
AI-парсинг PDF инвойсов:
- Использует Gemini, OpenRouter или DeepSeek
- Извлекает: обозначение, количество, описание
- Автоматический fallback на разные модели

Функция: `parse_invoice(pdf_path, method='auto', api_key=None)`

### S3 Service
Работа с хранилищем изображений:
- Загрузка файлов
- Генерация публичных URL
- Поддержка Cloudflare R2 и AWS S3

## Миграции БД

**Создать новую миграцию:**
```bash
alembic revision --autogenerate -m \"Description of changes\"
```

**Применить миграции:**
```bash
alembic upgrade head
```

**Откатить миграцию:**
```bash
alembic downgrade -1
```

## Environment Variables

См. `.env.example` для полного списка.

Обязательные:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
GEMINI_API_KEY=your_key  # или OPENROUTER_API_KEY
```

Опциональные (для S3/R2):
```env
S3_ENDPOINT=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET_NAME=...
```

## Логирование

Логи записываются в:
- `stdout` (консоль)
- `app.log` (файл)

Уровень логирования: `INFO`

Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Тестирование

Запуск тестов:
```bash
pytest
```

Тесты с покрытием:
```bash
pytest --cov=app tests/
```

Доступные тестовые скрипты:
- `test_db_connection.py` - Проверка подключения к БД
- `test_gen.py` - Тестирование генерации
- `test_full_cycle.py` - Полный цикл работы

## Разработка

### Code Style

Используйте:
- `black` для форматирования
- `ruff` для линтинга

```bash
black .
ruff check .
```

### Debugging

Запуск с дебаггером:
```bash
python -m debugpy --listen 5678 -m uvicorn app.main:app --reload
```

## Production

### Docker

```bash
docker build -t tamozh-backend .
docker run -p 8000:8000 --env-file .env tamozh-backend
```

### Cloud Run Deploy

```bash
./deploy_cloud_run.sh
```

## Troubleshooting

**Проблема:** Ошибка подключения к БД  
**Решение:** Проверьте `DATABASE_URL` и запущен ли PostgreSQL

**Проблема:** AI парсинг не работает  
**Решение:** Проверьте API ключи в `.env`

**Проблема:** Ошибки импорта  
**Решение:** Убедитесь что все зависимости установлены: `pip install -r requirements.txt`
