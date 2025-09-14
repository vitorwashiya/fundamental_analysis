"""
Test configuration and fixtures
"""
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from app.database.connection import Base, get_db


# Create test database
@pytest.fixture
def test_db():
    """Create a temporary database for testing"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Create engine and session
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Cleanup
    os.unlink(db_path)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_sector_data():
    """Sample sector data for testing"""
    return {
        "name": "Test Sector",
        "category": "Test Category",
        "subsectors": "Test Subsector 1,Test Subsector 2"
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing"""
    return {
        "symbol": "TEST4",
        "company_name": "Test Company S.A.",
        "sector_id": 1,
        "subsector": "Test Subsector",
        "cotacao": 10.50,
        "pl": 12.5,
        "pvp": 1.8,
        "div_yield": 5.2,
        "roic": 15.5,
        "roe": 18.2,
        "is_active": True
    }
