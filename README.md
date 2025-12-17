# Генератор Таможенных Документов

Веб-приложение для автоматической генерации таможенных документов на основе инвойсов с использованием AI для парсинга PDF.

## Описание

Система позволяет:
- ✅ Загружать PDF инвойсы и автоматически извлекать информацию с помощью AI (Gemini, OpenRouter)
- ✅ Сопоставлять товары с базой данных деталей
- ✅ Генерировать таможенные документы:
  - Техническое описание
  - Письмо о нестраховании
  - Уведомление по Решению 130
- ✅ Управлять базой данных деталей через веб-интерфейс

## Технологический стек

**Frontend:**
- Next.js 16 (App Router)
- React 19
- TypeScript
- Tailwind CSS v4

**Backend:**
- FastAPI
- Python 3.10+
- SQLAlchemy (async)
- PostgreSQL
- Alembic (migrations)

**AI & Integrations:**
- Google Gemini API
- OpenRouter API (Qwen 3 VL, DeepSeek V3)
- Cloudflare R2 / AWS S3

## Быстрый старт

Приложение поддерживает два варианта развертывания:

### Локальное развертывание (Docker)

Для разработки и тестирования локально с MinIO (S3-совместимое хранилище):

**Windows:**
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
Установите PostgreSQL локально или используйте Docker:
```bash
docker run -d \\
  --name tamozh-db \\
  -e POSTGRES_USER=postgres \\
  -e POSTGRES_PASSWORD=postgres \\
  -e POSTGRES_DB=tamozh_db \\
  -p 5432:5432 \\
  postgres:15
```

Примените миграции:
```bash
cd backend
alembic upgrade head
```

## Структура проекта

```
├── frontend/              # Next.js приложение
│   ├── src/
│   │   └── app/          # App Router
│   ├── public/           # Статические файлы
│   └── package.json
├── backend/              # FastAPI приложение
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── db/          # Модели БД
│   │   ├── services/    # Бизнес-логика
│   │   └── core/        # Конфигурация
│   ├── alembic/         # Миграции БД
│   ├── scripts/         # Утилиты
│   └── requirements.txt
├── docker-compose.yml    # Docker конфигурация
└── _изображения/        # Статические изображения товаров
```

## Основные функции

### 1. Загрузка и парсинг инвойсов
- Поддержка PDF файлов
- AI-парсинг через Gemini или OpenRouter
- Автоматическое извлечение: обозначений, количества, описаний

### 2. База данных деталей
- CRUD операции для деталей
- Поиск по обозначению и наименованию
- Хранение технических характеристик
- Привязка изображений

### 3. Генерация документов
- Техническое описание товаров
- Письмо о нестраховании
- Уведомление по Решению 130
- Экспорт в формате DOCX
- Опциональное добавление факсимиле (печать и подпись)

## API Endpoints

Полная документация доступна по адресу: http://localhost:8000/docs

Основные endpoints:
- `POST /api/v1/invoices/upload` - Загрузка и парсинг PDF
- `POST /api/v1/invoices/generate` - Генерация документов
- `GET /api/v1/parts` - Получение списка деталей
- `POST /api/v1/parts` - Создание/обновление детали
- `PUT /api/v1/parts/{id}` - Обновление детали

## Переменные окружения

См. [`backend/.env.example`](backend/.env.example) для полного списка.

Обязательные:
- `DATABASE_URL` - Connection string для PostgreSQL
- `GEMINI_API_KEY` или `OPENROUTER_API_KEY` - API ключи для AI

Опциональные:
- `S3_*` - конфигурация для хранения изображений в S3/R2

## Разработка

### Миграции БД

Создать новую миграцию:
```bash
cd backend
alembic revision --autogenerate -m "Description"
```

Применить миграции:
```bash
alembic upgrade head
```

### Линтинг

**Frontend:**
```bash
cd frontend
npm run lint
```

**Backend:**
```bash
cd backend
black .
ruff check .
```

## Деплой

### Production с Docker

1. Обновите переменные окружения для production
2. Используйте production docker-compose:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Cloud Run (GCP)
См. скрипты деплоя:
- `backend/deploy_cloud_run.sh`
- `backend/deploy_cloud_run.ps1`

## Тестирование

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

## Лицензия

[Укажите лицензию]

## Авторы

[Укажите авторов]

## Поддержка

При возникновении проблем создайте issue в репозитории.
