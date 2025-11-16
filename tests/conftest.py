import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_session():
    """Sample reconciliation session data"""
    return {
        "session_name": "test_finance_vs_stripe",
        "system_a_name": "Finance System",
        "system_b_name": "Stripe",
        "description": "Test reconciliation session"
    }


@pytest.fixture
def sample_system_a_transactions():
    """Sample transactions from System A (Finance)"""
    return {
        "transactions": [
            {"transaction_id": "TXN-101", "system": "system_a", "amount": 100.00, "transaction_metadata": "Payment A"},
            {"transaction_id": "TXN-102", "system": "system_a", "amount": 200.00, "transaction_metadata": "Payment B"},
            {"transaction_id": "TXN-103", "system": "system_a", "amount": 300.00, "transaction_metadata": "Payment C"},
            {"transaction_id": "TXN-104", "system": "system_a", "amount": 400.00, "transaction_metadata": "Payment D"},
            {"transaction_id": "TXN-105", "system": "system_a", "amount": 500.00, "transaction_metadata": "Payment E"}
        ]
    }


@pytest.fixture
def sample_system_b_transactions():
    """Sample transactions from System B (Stripe)"""
    return {
        "transactions": [
            {"transaction_id": "TXN-101", "system": "system_b", "amount": 100.00, "transaction_metadata": "Stripe confirmed"},
            {"transaction_id": "TXN-102", "system": "system_b", "amount": 200.00, "transaction_metadata": "Stripe confirmed"},
            {"transaction_id": "TXN-103", "system": "system_b", "amount": 300.00, "transaction_metadata": "Stripe confirmed"},
            {"transaction_id": "TXN-106", "system": "system_b", "amount": 600.00, "transaction_metadata": "Stripe confirmed"}
        ]
    }