import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.patient import Patient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test_patients.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    db = TestingSessionLocal()
    user = User(
        email="staff@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Staff User",
        role=UserRole.STAFF
    )
    db.add(user)
    db.commit()
    db.close()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "staff@example.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_patient(auth_headers):
    response = client.post(
        "/api/v1/patients/",
        headers=auth_headers,
        json={
            "full_name": "John Doe",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
            "phone": "+1234567890",
            "email": "john@example.com"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert "patient_id" in data

def test_list_patients(auth_headers):
    # Create a patient first
    db = TestingSessionLocal()
    patient = Patient(
        patient_id="P2024000001",
        full_name="Jane Doe",
        date_of_birth=date(1985, 5, 15),
        gender="Female",
        phone="+1987654321"
    )
    db.add(patient)
    db.commit()
    db.close()
    
    response = client.get("/api/v1/patients/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["full_name"] == "Jane Doe"

def test_search_patients(auth_headers):
    db = TestingSessionLocal()
    patient = Patient(
        patient_id="P2024000002",
        full_name="Bob Smith",
        date_of_birth=date(1980, 3, 20),
        gender="Male",
        phone="+1555666777"
    )
    db.add(patient)
    db.commit()
    db.close()
    
    response = client.get(
        "/api/v1/patients/",
        params={"search": "Bob"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "Bob" in data[0]["full_name"]
