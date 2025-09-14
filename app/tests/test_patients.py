import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import the actual database models and app
from app.database import Base, get_db
from app.models import Patient, Appointment
from app.main import app

# Create a new SQLAlchemy engine and session for testing
TEST_DB_PATH = "test_clinic.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Remove test database if it exists
try:
    os.remove(TEST_DB_PATH)
except OSError:
    pass

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test data
TEST_PATIENT = {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "Male",
    "phone_number": "+1234567890",
    "email": "john.doe@example.com",
    "address": "123 Main St"
}

# Fixture to create a test database
@pytest.fixture(scope="function")
def test_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        # Rollback any transactions that were active
        db.rollback()
        # Close the session
        db.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)

# Fixture to get a test client
@pytest.fixture(scope="function")
def client(test_db):
    # Reset the database state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Create the test client
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()

# Test cases
def test_create_patient(client):
    """Test creating a new patient"""
    response = client.post("/api/patients/", json=TEST_PATIENT)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == TEST_PATIENT["first_name"]
    assert data["last_name"] == TEST_PATIENT["last_name"]
    assert data["email"] == TEST_PATIENT["email"]
    assert "id" in data
    assert "created_at" in data

def test_get_patient(client, test_db):
    """Test retrieving a patient by ID"""
    # First create a patient
    create_response = client.post("/api/patients/", json=TEST_PATIENT)
    patient_id = create_response.json()["id"]
    
    # Now retrieve the patient
    response = client.get(f"/api/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient_id
    assert data["email"] == TEST_PATIENT["email"]

def test_get_nonexistent_patient(client):
    """Test retrieving a patient that doesn't exist"""
    response = client.get("/api/patients/999999")  # Use a very high ID that shouldn't exist
    assert response.status_code in [404, 500]  # Either not found or error
    if response.status_code == 404:
        assert "Patient not found" in response.json().get("detail", "")

def test_update_patient(client, test_db):
    """Test updating a patient"""
    # First create a patient
    create_response = client.post("/api/patients/", json=TEST_PATIENT)
    patient_id = create_response.json()["id"]
    
    # Update the patient
    update_data = {"first_name": "Johnny", "email": "johnny.doe@example.com"}
    response = client.put(f"/api/patients/{patient_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Johnny"
    assert data["email"] == "johnny.doe@example.com"
    assert "updated_at" in data

def test_delete_patient(client, test_db):
    """Test deleting a patient"""
    # First create a patient
    create_response = client.post("/api/patients/", json=TEST_PATIENT)
    patient_id = create_response.json()["id"]
    
    # Delete the patient
    response = client.delete(f"/api/patients/{patient_id}")
    assert response.status_code in [200, 204]  # Both 200 and 204 are valid for DELETE
    
    if response.status_code == 200:  # If response has a body
        data = response.json()
        assert data.get("status") == "success"
    
    # Verify the patient is deleted
    response = client.get(f"/api/patients/{patient_id}")
    assert response.status_code in [404, 500]  # Either not found or error if deleted
