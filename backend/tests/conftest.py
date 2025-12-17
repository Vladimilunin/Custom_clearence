"""
Pytest configuration and fixtures for TamozhGen tests.
Supports both unit tests and integration tests with real API calls.
"""
import pytest
import os
import sys
from typing import Generator
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.session import get_db
from app.db import models as db_models

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables without schema for SQLite
# We need to remove the schema from table_args
def create_test_tables():
    """Create test tables without schema for SQLite compatibility."""
    # Get the original Part table
    original_table_args = getattr(db_models.Part, '__table_args__', None)
    
    # Temporarily remove schema
    if isinstance(original_table_args, dict) and 'schema' in original_table_args:
        # Create table without schema
        from sqlalchemy import Table, MetaData
        metadata = MetaData()
        
        # Create a simple parts table for testing
        from sqlalchemy.sql import text
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    designation TEXT UNIQUE NOT NULL,
                    name TEXT,
                    material TEXT,
                    weight REAL,
                    weight_unit TEXT,
                    dimensions TEXT,
                    description TEXT,
                    section TEXT,
                    image_path TEXT,
                    manufacturer TEXT,
                    condition TEXT,
                    component_type TEXT,
                    specs TEXT,
                    current_type TEXT,
                    input_voltage TEXT,
                    input_current TEXT,
                    processor TEXT,
                    ram_kb INTEGER,
                    rom_mb INTEGER,
                    tnved_code TEXT,
                    tnved_description TEXT
                )
            """))
            conn.commit()


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database for each test."""
    create_test_tables()
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up tables
        from sqlalchemy.sql import text
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS parts"))
            conn.commit()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client with database dependency override."""
    async def override_get_db():
        # Return a sync wrapper for the async dependency
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Patch the Part model's table to use the test database without schema
    original_table_args = db_models.Part.__table_args__
    db_models.Part.__table_args__ = {}
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        db_models.Part.__table_args__ = original_table_args
        app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def project_root() -> str:
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def fixtures_dir() -> str:
    """Get fixtures directory path."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture(scope="session")
def test_pdf_path(fixtures_dir) -> str | None:
    """Get path to a test PDF file if available."""
    pdf_files = [
        os.path.join(fixtures_dir, "3_PI For Алексей Семенов- 20241225.pdf"),
        os.path.join(fixtures_dir, "PI PTJ20251023B1.pdf"),
        os.path.join(fixtures_dir, "Revised PI_Shenzhen_Wofly 20231016.pdf"),
    ]
    
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            return pdf_path
    
    return None


@pytest.fixture
def sample_invoice_1(fixtures_dir) -> str:
    """Path to first sample invoice."""
    path = os.path.join(fixtures_dir, "3_PI For Алексей Семенов- 20241225.pdf")
    if not os.path.exists(path):
        pytest.skip(f"Test PDF not found: {path}")
    return path


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may use external APIs)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

