# Руководство по разработке, тестированию и развертыванию

## Содержание

1. [Локальная разработка](#локальная-разработка)
2. [Тестирование](#тестирование)
3. [Развертывание](#развертывание)
4. [Рабочий процесс](#рабочий-процесс)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Локальная разработка

### Быстрый старт

**Windows:**
```powershell
.\scripts\start-local.ps1
```

**Linux/Mac:**
```bash
./scripts/start-local.sh
```

Это автоматически:
- Запустит все 4 сервиса (frontend, backend, db, minio)
- Инициализирует MinIO bucket
- Применит миграции БД
- Выведет URLs всех сервисов

### Доступные сервисы

| Сервис | URL | Назначение |
|--------|-----|------------|
| Frontend | http://localhost:3000 | Next.js UI |
| Backend API | http://localhost:8001 | FastAPI |
| API Docs | http://localhost:8001/docs | Swagger UI |
| PostgreSQL | localhost:5432 | База данных |
| MinIO Console | http://localhost:9001 | S3 хранилище |

**MinIO credentials:**
- Username: `minioadmin`
- Password: `minioadmin`

### Структура проекта

```
.
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Конфигурация
│   │   ├── models/        # SQLAlchemy модели
│   │   ├── schemas/       # Pydantic схемы
│   │   └── services/      # Бизнес-логика
│   ├── alembic/           # Миграции БД
│   ├── tests/             # Тесты
│   └── Dockerfile
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   └── components/   # React компоненты
│   └── Dockerfile
├── scripts/              # Скрипты автоматизации
├── _изображения/         # Изображения деталей
└── docker-compose.yml
```

### Разработка Backend

#### Установка зависимостей

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Запуск в dev режиме (без Docker)

```bash
# Настройте .env файл
cp .env.local.example .env
# Отредактируйте .env

# Запустите Postgres и MinIO через Docker
docker-compose up -d db minio

# Запустите backend локально
uvicorn app.main:app --reload --port 8001
```

#### Создание миграции БД

```bash
cd backend
alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head
```

#### Добавление нового endpoint

1. Создайте схему в `app/schemas/`
2. Добавьте endpoint в `app/api/endpoints/`
3. Зарегистрируйте router в `app/api/api.py`
4. Добавьте тесты в `tests/`

**Пример:**

```python
# app/schemas/invoice.py
from pydantic import BaseModel

class InvoiceUploadResponse(BaseModel):
    items: list
    debug_info: dict

# app/api/endpoints/invoices.py
from fastapi import APIRouter, UploadFile

router = APIRouter()

@router.post("/upload")
async def upload_invoice(file: UploadFile):
    # Ваша логика
    return {"status": "success"}
```

### Разработка Frontend

#### Установка зависимостей

```bash
cd frontend
npm install
```

#### Запуск в dev режиме

```bash
npm run dev
```

Откроется на http://localhost:3000

#### Добавление новой страницы

```bash
# App Router
frontend/src/app/new-page/page.tsx
```

#### Добавление компонента

```bash
# Компонент
frontend/src/components/MyComponent.tsx
```

**Пример:**

```tsx
// src/components/InvoiceUploader.tsx
'use client';

import { useState } from 'react';

export default function InvoiceUploader() {
  const [file, setFile] = useState<File | null>(null);
  
  const handleUpload = async () => {
    // Ваша логика
  };
  
  return (
    <div>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}
```

### Работа с изображениями

#### Локально (MinIO)

Изображения хранятся в MinIO bucket `tamozh-images`.

**Загрузка изображений:**

```powershell
# Загрузить все изображения из папки
Get-ChildItem "_изображения" -Include "*.jpg","*.webp","*.png" -Recurse | 
  ForEach-Object { C:\tools\mc.exe cp $_.FullName "local/tamozh-images/$($_.Name)" }
```

**Доступ к изображениям:**
```
http://localhost:9000/tamozh-images/{filename}
```

#### Облако (R2/S3)

В production изображения загружаются в Cloudflare R2.

**URL формат:**
```
https://pub-{account-id}.r2.dev/{filename}
```

### Логи и отладка

**Docker логи:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs backend --tail 100
```

**Backend логи внутри контейнера:**
```bash
docker-compose exec backend cat /tmp/backend.log
```

**PostgreSQL:**
```bash
docker-compose exec db psql -U postgres -d tamozh_db
```

---

## Тестирование

### Backend тесты

#### Запуск всех тестов

```bash
cd backend
pytest
```

#### Запуск с coverage

```bash
pytest --cov=app --cov-report=html
```

Отчет будет в `htmlcov/index.html`

#### Запуск конкретного теста

```bash
pytest tests/test_invoices.py::test_upload_invoice
```

#### Тестирование API вручную

**Через Swagger UI:**
http://localhost:8001/docs

**Через curl:**
```bash
curl -X POST http://localhost:8001/api/v1/invoices/upload \
  -F "file=@test.pdf" \
  -F "parsing_method=openrouter_qwen"
```

**Через Python скрипт:**
```bash
python test_pdf_upload.py
```

### Frontend тесты

```bash
cd frontend
npm test
```

### E2E тесты

Создайте Playwright тесты для полного флоу:

```typescript
// tests/e2e/invoice-upload.spec.ts
import { test, expect } from '@playwright/test';

test('upload invoice', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('test.pdf');
  
  await page.click('button:has-text("Загрузить")');
  
  await expect(page.locator('.results')).toBeVisible();
});
```

### Тестовые данные

**Тестовый PDF:**
```
PI PTJ20251023B1.pdf  # В корне проекта
```

**Тестовая база:**
- 114 деталей уже загружены
- Проверить: `docker-compose exec db psql -U postgres -d tamozh_db -c "SELECT COUNT(*) FROM parts;"`

### Методы парсинга для тестирования

| Метод | API | Скорость | Точность |
|-------|-----|----------|----------|
| `openrouter_qwen` | OpenRouter | ⚡ Быстро | ⭐⭐⭐⭐ |
| `openrouter_gemini` | OpenRouter | ⚡ Быстро | ⭐⭐⭐⭐⭐ |
| `siliconflow_qwen` | SiliconFlow | ⚡⚡ Очень быстро | ⭐⭐⭐⭐ |
| `deepseek_v3` | DeepSeek | 🐌 Медленно | ⭐⭐⭐ |

**По умолчанию:** `openrouter_qwen` (бесплатный)

---

## Развертывание

### Локальное развертывание (Docker)

Уже настроено! Используйте:

```powershell
.\scripts\start-local.ps1
```

Это полноценное окружение с:
- PostgreSQL базой
- MinIO S3 хранилищем
- Backend API
- Frontend UI

### Облачное развертывание

#### Предварительные требования

1. **Google Cloud Project** для backend
2. **Vercel Account** для frontend
3. **Cloudflare R2** или **AWS S3** для хранилища изображений
4. **Neon PostgreSQL** (уже настроен) или **Cloud SQL**

#### 1. Развертывание Backend на Cloud Run

```powershell
cd backend
.\deploy_cloud_run.ps1
```

Скрипт автоматически:
1. Загрузит credentials из `.env.cloud`
2. Соберет Docker image
3. Загрузит в Google Container Registry
4. Задеплоит на Cloud Run
5. Настроит environment variables
6. Выведет Service URL

**Проверка:**
```bash
curl https://backend-service-xxxxx-uc.a.run.app/
```

#### 2. Развертывание Frontend на Vercel

```powershell
.\scripts\deploy-frontend-vercel.ps1
```

**После деплоя:**

1. Зайдите в Vercel Dashboard
2. Перейдите в Settings → Environment Variables
3. Добавьте:
   ```
   NEXT_PUBLIC_API_URL=https://backend-service-xxxxx-uc.a.run.app
   ```
4. Redeploy frontend

#### 3. Настройка Cloudflare R2

**Создание bucket:**
```bash
# Через Cloudflare Dashboard
# Buckets → Create bucket → "customs-images"
```

**Загрузка изображений:**
```bash
# Используйте rclone или AWS CLI
rclone copy _изображения r2:customs-images/
```

**Настройка public access:**
- Settings → Public Access → Enable
- Получите public URL: `https://pub-{id}.r2.dev`

### CI/CD Pipeline

#### GitHub Actions (пример)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Cloud Run
        run: |
          cd backend
          ./deploy_cloud_run.sh
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GCP_SA_KEY }}
          
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

### Мониторинг

#### Cloud Run

```bash
# Логи
gcloud run services logs read backend-service --region=us-central1

# Метрики
gcloud run services describe backend-service --region=us-central1
```

#### Vercel

- Dashboard → Deployments → Logs
- Analytics tab для метрик

---

## Рабочий процесс

### Feature Development Workflow

1. **Создать ветку:**
   ```bash
   git checkout -b feature/invoice-metadata
   ```

2. **Разработка локально:**
   - Запустить `.\scripts\start-local.ps1`
   - Внести изменения
   - Тестировать

3. **Создать миграцию (если нужно):**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add invoice metadata"
   alembic upgrade head
   ```

4. **Тесты:**
   ```bash
   cd backend
   pytest
   ```

5. **Коммит:**
   ```bash
   git add .
   git commit -m "feat: добавить метаданные инвойса"
   ```

6. **Push и PR:**
   ```bash
   git push origin feature/invoice-metadata
   ```

### Hotfix Workflow

1. **Создать hotfix ветку:**
   ```bash
   git checkout -b hotfix/parsing-error
   ```

2. **Исправить проблему**

3. **Тестировать локально**

4. **Задеплоить напрямую:**
   ```bash
   cd backend
   .\deploy_cloud_run.ps1
   ```

5. **Merge в main**

---

## Best Practices

### Backend

#### 1. Используйте type hints

```python
def parse_invoice(pdf_path: str, method: str = "auto") -> tuple[list[dict], dict]:
    ...
```

#### 2. Валидация через Pydantic

```python
from pydantic import BaseModel, validator

class InvoiceItem(BaseModel):
    designation: str
    name: str | None = None
    
    @validator('designation')
    def designation_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Designation cannot be empty')
        return v
```

#### 3. Обработка ошибок

```python
from fastapi import HTTPException

try:
    result = parse_invoice(pdf_path)
except FileNotFoundError:
    raise HTTPException(status_code=404, detail="PDF not found")
except Exception as e:
    logger.error(f"Parsing failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

#### 4. Логирование

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Processing invoice: {filename}")
logger.error(f"Failed to parse: {error}")
```

### Frontend

#### 1. Используйте TypeScript

```tsx
interface InvoiceItem {
  designation: string;
  name?: string;
  material?: string;
}

const items: InvoiceItem[] = [];
```

#### 2. Server vs Client Components

```tsx
// Server Component (default)
async function InvoicePage() {
  const data = await fetch('...');
  return <div>{data}</div>;
}

// Client Component (интерактивность)
'use client';
function InvoiceUploader() {
  const [file, setFile] = useState<File | null>(null);
  ...
}
```

#### 3. Error boundaries

```tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Что-то пошло не так!</h2>
      <button onClick={() => reset()}>Попробовать снова</button>
    </div>
  );
}
```

### Database

#### 1. Индексы для частых запросов

```python
class Part(Base):
    __tablename__ = "parts"
    
    designation = Column(String, index=True)  # Часто ищем по designation
```

#### 2. Миграции

- Всегда проверяйте миграции перед применением
- Делайте backup перед миграциями в production
- Используйте `alembic downgrade` для отката

#### 3. Транзакции

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def update_part(db: AsyncSession, part_id: int, data: dict):
    async with db.begin():
        part = await db.get(Part, part_id)
        for key, value in data.items():
            setattr(part, key, value)
        await db.commit()
```

### Security

#### 1. Environment Variables

- ❌ Никогда не коммитить `.env` файлы
- ✅ Использовать `.env.example` как шаблон
- ✅ Хранить secrets в Secret Manager (production)

#### 2. API Keys

- Используйте разные ключи для dev/prod
- Регулярно ротируйте ключи
- Мониторьте использование

#### 3. CORS

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Backend не запускается

**Проблема:** `Cannot connect to database`

**Решение:**
```bash
# Проверить что PostgreSQL запущен
docker-compose ps db

# Перезапустить
docker-compose restart db

# Проверить логи
docker-compose logs db
```

**Проблема:** `Module not found`

**Решение:**
```bash
# Переустановить зависимости
cd backend
pip install -r requirements.txt --force-reinstall
```

### Frontend не подключается к API

**Проблема:** `Network error`

**Решение:**
```bash
# Проверить NEXT_PUBLIC_API_URL в .env
cat frontend/.env

# Должно быть: NEXT_PUBLIC_API_URL=http://localhost:8001

# Перезапустить frontend
docker-compose restart frontend
```

### MinIO bucket пуст

**Решение:**
```powershell
# Загрузить изображения
Get-ChildItem "_изображения" -Include "*.jpg","*.webp","*.png" -Recurse | 
  ForEach-Object { C:\tools\mc.exe cp $_.FullName "local/tamozh-images/$($_.Name)" }
```

### Миграции не применяются

**Проблема:** `Target database is not up to date`

**Решение:**
```bash
cd backend
alembic upgrade head

# Если не помогает
alembic downgrade -1
alembic upgrade head
```

### Cloud Run деплой fails

**Проблема:** `Permission denied`

**Решение:**
```bash
# Авторизоваться заново
gcloud auth login
gcloud config set project tamozh-backend-479110

# Проверить права
gcloud projects get-iam-policy tamozh-backend-479110
```

### Out of memory в Cloud Run

**Решение:**
```bash
# Увеличить память в deploy скрипте
--memory 2Gi  # Вместо 1Gi
```

---

## Дополнительные ресурсы

### Документация

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/docs)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [MinIO](https://min.io/docs/)
- [Cloud Run](https://cloud.google.com/run/docs)
- [Vercel](https://vercel.com/docs)

### Инструменты

- **API Testing:** Postman, Insomnia
- **Database:** DBeaver, pgAdmin
- **Monitoring:** Google Cloud Console, Vercel Analytics
- **Logs:** `docker-compose logs`, Cloud Logging

### Контакты и поддержка

- GitHub Issues для багов
- Документация проекта в `/docs`
- README.md для быстрого старта

---

## Заключение

Это руководство покрывает основные аспекты разработки, тестирования и развертывания. При возникновении вопросов:

1. Проверьте этот документ
2. Посмотрите `DEPLOYMENT.md` для деталей развертывания
3. Проверьте логи сервисов
4. Создайте GitHub Issue

**Удачной разработки! 🚀**
