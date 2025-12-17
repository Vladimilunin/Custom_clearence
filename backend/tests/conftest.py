"""Pytest configuration and fixtures."""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test base without schema constraint
TestBase = declarative_base()

class Part(TestBase):
    """Test Part model without schema for SQLite compatibility."""
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True, index=True)
    designation = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    material = Column(String, nullable=True)
    weight = Column(Float, nullable=True)
    dimensions = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    section = Column(String, nullable=True)
    image_path = Column(String, nullable=True)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database for each test."""
    TestBase.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        TestBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
