# Backend Tests

This directory contains tests for the FastAPI backend.

## Structure

```
tests/
├── __init__.py
├── conftest.py       # Pytest fixtures
├── test_api/         # API endpoint tests
├── test_services/    # Service layer tests
└── test_db/          # Database tests
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_api/test_parts.py
```
