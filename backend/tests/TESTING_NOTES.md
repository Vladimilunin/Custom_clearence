# Проблема с Unit-тестами

## Описание

Unit-тесты не могут работать с in-memory SQLite из-за использования PostgreSQL-specific features в модели `Part`:

```python
class Part(Base):
    __tablename__ = "parts"
    __table_args__ = {"schema": "public"}  # ← Не поддерживается в SQLite
```

SQLite не поддерживает схемы (schemas), поэтому создание таблицы с `schema="public"` выдает ошибку:
```
sqlite3.OperationalError: unknown database public
```

## Решения

### Вариант 1: Использовать PostgreSQL для тестов (рекомендуется)

Запускать тесты с реальной PostgreSQL БД в Docker:

```yaml
# docker-compose.test.yml
services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test_db
    ports:
      - "5433:5432"
```

```bash
docker-compose -f docker-compose.test.yml up -d
pytest
docker-compose -f docker-compose.test.yml down
```

### Вариант 2: Условная схема для моделей

Изменить модель для поддержки обеих БД:

```python
import os

class Part(Base):
    __tablename__ = "parts"
    __table_args__ = {} if os.getenv("TESTING") else {"schema": "public"}
```

### Вариант 3: Обойти через monkey-patching (текущий подход)

Создать отдельную тестовую модель без схемы (уже реализовано в `conftest.py`), но это не работает полностью из-за импортов в endpoints.

## Текущее состояние

Создана инфраструктура тестирования:
- ✅ `pytest` настроен
- ✅ Fixtures созданы
- ✅ Примеры тестов написаны
- ❌ Тесты не проходят из-за PostgreSQL-specific схемы

## Рекомендация

Для production использовать **Вариант 1** с PostgreSQL в Docker для тестов.
