# Руководство по развертыванию

Это руководство описывает два варианта развертывания приложения:
1. **Локальное развертывание** (Docker + MinIO + PostgreSQL)
2. **Облачное развертывание** (Vercel + Cloud Run + Neon PostgreSQL + Cloudflare R2)

---

## Сравнение вариантов

| Функция | Локальное | Облачное |
|---------|-----------|----------|
| **Сложность** | Низкая | Средняя |
| **Стоимость** | Бесплатно | Платно (зависит от использования) |
| **Производительность** | Зависит от hardware | Высокая |
| **Масштабируемость** | Ограничена | Авто-масшт абирование |
| **Хранилище изображений** | MinIO (локально) | S3/R2 (облако) |
| **База данных** | PostgreSQL (Docker) | Neon PostgreSQL (serverless) |
| **Использование** | Разработка, тестирование | Production |

---

##  1. Локальное развертывание (Docker)

### Требования

- Docker Desktop (Windows/Mac) или Docker Engine (Linux)
- Docker Compose
- 8 GB RAM minimum
- 10 GB свободного места

### Быстрый старт

**Windows (PowerShell):**
```powershell
.\scripts\start-local.ps1
```

**Linux/Mac (Bash):**
```bash
chmod +x scripts/*.sh
./scripts/start-local.sh
```

### Что происходит автоматически:

1. ✅ Останавливает существующие контейнеры
2. ✅ Собирает и запускает все сервисы (frontend, backend, db, minio)
3. ✅ Ждет готовности всех healthchecks
4. ✅ Инициализирует MinIO bucket (`tamozh-images`)
5. ✅ Применяет миграции базы данных

### Сервисы

После успешного запуска доступны:

| Сервис | URL | Логин |
|--------|-----|-------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8001 | - |
| API Documentation | http://localhost:8001/docs | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| PostgreSQL | localhost:5432 | postgres / postgres |

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Остановка

**Windows:**
```powershell
.\scripts\stop-local.ps1
```

**Linux/Mac:**
```bash
./scripts/stop-local.sh
```

### Полная очистка (включая данные)

```bash
docker-compose down -v
```

> [!WARNING]
> Это удалит ВСЕ данные из базы данных и MinIO!

---

## 2. Облачное развертывание

### Требования

- Google Cloud Platform аккаунт (для Cloud Run)
- Vercel аккаунт (для frontend)
- Cloudflare R2 или AWS S3 (для хранения изображений)
- Cloud SQL или managed PostgreSQL

### Подготовка

#### 2.1 Настройка хранилища изображений (R2/S3)

**Cloudflare R2:**
1. Создайте bucket в R2 Dashboard
2. Получите Access Key ID и Secret Access Key
3. Настройте публичный домен (опционально)

**AWS S3:**
1. Создайте bucket в AWS Console
2. Настройте IAM пользователя с S3 доступом
3. Настройте bucket policy для публичного чтения

#### 2.2 Настройка базы данных

**Neon PostgreSQL (рекомендуется):**

Уже настроено! В `.env.cloud` используется Neon:
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:***@ep-bitter-night-ahz06l2w-pooler.c-3.us-east-1.aws.neon.tech/neondb?ssl=require
```

**Преимущества Neon:**
- ✅ Serverless (автоматическое масштабирование)
- ✅ Branching (ветки БД для разработки)
- ✅ Быстрый старт (не нужно настраивать)
- ✅ Free tier (достаточно для начала)

**Альтернатива - Cloud SQL (GCP):**
```bash
gcloud sql instances create tamozh-db \\
  --database-version=POSTGRES_15 \\
  --tier=db-f1-micro \\
  --region=us-central1
```

### Развертывание Backend (Cloud Run)

**Предварительная настройка:**

1. Установите gcloud CLI
2. Авторизуйтесь:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Настройте environment variables в [`backend/.env`](file:///d:/Work/_develop/_gen_for_%20tamozh/_dev/backend/.env):
   ```bash
   cp .env.cloud.example backend/.env
   # Отредактируйте backend/.env
   ```

**Windows:**
```powershell
cd backend
.\deploy_cloud_run.ps1
```

**Linux/Mac:**
```bash
cd backend
chmod +x deploy_cloud_run.sh
./deploy_cloud_run.sh
```

**Что происходит:**
1. Собирается Docker image
2. Push в Google Container Registry
3. Деплой на Cloud Run
4. Настраиваются environment variables

**Скопируйте URL backend** из вывода скрипта (нужен для frontend).

### Развертывание Frontend (Vercel)

**Предварительная настройка:**

1. Установите Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Авторизуйтесь:
   ```bash
   vercel login
   ```

**Windows:**
```powershell
.\scripts\deploy-frontend-vercel.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/deploy-frontend-vercel.sh
./scripts/deploy-frontend-vercel.sh
```

**После деплоя:**

Настройте environment variable в Vercel Dashboard:
- `NEXT_PUBLIC_API_URL` = URL вашего backend на Cloud Run

### Проверка облачного деплоя

1. Откройте URL frontend от Vercel
2. Проверьте что API работает (загрузите тестовый инвойс)
3. Убедитесь что изображения загружаются в R2/S3

---

## Environment Variables

### Локальное окружение

Пример в [`.env.local.example`](file:///d:/Work/_develop/_gen_for_%20tamozh/_dev/.env.local.example):

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tamozh_db

# AI API Keys
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# MinIO (Local S3)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=tamozh-images
S3_PUBLIC_DOMAIN=http://localhost:9000
```

### Облачное окружение

Пример в [`.env.cloud.example`](file:///d:/Work/_develop/_gen_for_%20tamozh/_dev/.env.cloud.example):

```env
# Database (Neon PostgreSQL - уже настроен)
DATABASE_URL=postgresql+asyncpg://neondb_owner:***@ep-bitter-night-ahz06l2w-pooler.c-3.us-east-1.aws.neon.tech/neondb?ssl=require

# AI API Keys
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Cloudflare R2
S3_ENDPOINT=https://account-id.r2.cloudflarestorage.com
S3_ACCESS_KEY=your_r2_access_key
S3_SECRET_KEY=your_r2_secret_key
S3_BUCKET_NAME=tamozh-images
S3_PUBLIC_DOMAIN=https://your-domain.com
```

---

## Миграции базы данных

### Локально

Автоматически применяются при `start-local.sh/ps1`.

Вручную:
```bash
docker-compose exec backend alembic upgrade head
```

### Облачно (Cloud Run)

Запустите миграции после деплоя:
```bash
gcloud run jobs create migrations \\
  --image=gcr.io/YOUR_PROJECT/tamozh-backend \\
  --command="alembic,upgrade,head" \\
  --set-env-vars DATABASE_URL=...

gcloud run jobs execute migrations
```

---

## Troubleshooting

### Локальное развертывание

**Проблема:** Порты заняты
```
Error: Port 3000/8001/9000 already allocated
```
**Решение:** Остановите процессы на этих портах или измените порты в `docker-compose.yml`

**Проблема:** MinIO не инициализируется
```
Error: Connection refused to MinIO
```
**Решение:** 
1. Проверьте что MinIO container запущен: `docker-compose ps`
2. Подождите 30 секунд и попробуйте снова
3. Проверьте логи: `docker-compose logs minio`

**Проблема:** Frontend не подключается к backend
```
Network Error
```
**Решение:** Убедитесь что `NEXT_PUBLIC_API_URL=http://localhost:8001` в environment

### Облачное развертывание

**Проблема:** Cloud Run deployment fails
```
Error: Permission denied
```
**Решение:** 
1. Проверьте права IAM
2. Enable Cloud Run API
3. Enable Container Registry API

**Проблема:** CORS errors
```
Access-Control-Allow-Origin error
```
**Решение:** Добавьте Vercel URL в `origins` в [`backend/app/main.py`](file:///d:/Work/_develop/_gen_for_%20tamozh/_dev/backend/app/main.py)

**Проблема:** Images not loading from R2/S3
```
Image URL returns 403
```
**Решение:** 
1. Проверьте bucket policy (должен быть public read)
2. Проверьте CORS настройки bucket
3. Убедитесь что `S3_PUBLIC_DOMAIN` настроен правильно

---

## Переключение между режимами

### Из локального в облачный:

1. Остановите локальные сервисы
2. Обновите `.env` на облачные настройки
3. Задеплойте в облако

### Из облачного в локальный:

1. Обновите `.env` на локальные настройки
2. Запустите `start-local.sh/ps1`

---

## Backup и восстановление

### Локальная база данных

**Backup:**
```bash
docker-compose exec -T db pg_dump -U postgres tamozh_db > backup.sql
```

**Restore:**
```bash
cat backup.sql | docker-compose exec -T db psql -U postgres tamozh_db
```

### MinIO данные

**Backup:**
```bash
mc mirror local/tamozh-images ./backup/images
```

---

## Мониторинг

### Локально

**Проверка здоровья сервисов:**
```bash
docker-compose ps
```

**Использование ресурсов:**
```bash
docker stats
```

### Облачно

**Cloud Run:**
- Logs: Cloud Console → Cloud Run → Logs
- Metrics: Cloud Console → Cloud Run → Metrics

**Vercel:**
- Analytics: Vercel Dashboard → Analytics
- Logs: Vercel Dashboard → Deployments → Logs

---

## Дополнительные ресурсы

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MinIO Documentation](https://min.io/docs/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
