import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

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
from app import schemas

# Create a new SQLAlchemy engine and session for testing
TEST_DB_PATH = "test_clinic_appointments.db"
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

def get_future_date(days=1):
    return (datetime.now() + timedelta(days=days)).isoformat()

TEST_APPOINTMENT = {
    "patient_id": 1,  # Will be set in the test
    "appointment_date": get_future_date(1),
    "status": "scheduled",
    "description": "Initial consultation"  # Changed from 'notes' to 'description' to match schema
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
    with TestClient(app) as test_client:
        yield test_client

# Helper function to create a test patient
def create_test_patient(client):
    response = client.post("/api/patients/", json=TEST_PATIENT)
    return response.json()["id"]

# Test appointment endpoints
def test_create_appointment(client):
    """Test creating a new appointment"""
    # First create a patient
    patient_id = create_test_patient(client)
    
    # Create appointment data with the patient ID
    appointment_data = TEST_APPOINTMENT.copy()
    appointment_data["patient_id"] = patient_id
    
    # Create the appointment
    response = client.post("/api/appointments/", json=appointment_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["patient_id"] == patient_id
    assert data["status"] == "scheduled"
    assert "id" in data
    assert "created_at" in data
    # updated_at might be None for newly created records
    assert data.get("updated_at") is None or isinstance(data["updated_at"], str)

def test_get_appointment(client):
    """Test retrieving an appointment by ID"""
    # First create a patient and an appointment
    patient_id = create_test_patient(client)
    
    # Create appointment data
    appointment_data = TEST_APPOINTMENT.copy()
    appointment_data["patient_id"] = patient_id
    
    # Create the appointment
    create_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = create_response.json()["id"]
    
    # Retrieve the appointment
    response = client.get(f"/api/appointments/{appointment_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == appointment_id
    assert data["patient_id"] == patient_id
    # updated_at might be None for newly created records
    assert data.get("updated_at") is None or isinstance(data["updated_at"], str)

def test_get_nonexistent_appointment(client):
    """Test retrieving an appointment that doesn't exist"""
    response = client.get("/api/appointments/999999")
    assert response.status_code == 404
    assert "Appointment not found" in response.json()["detail"]

def test_update_appointment(client):
    """Test updating an appointment"""
    # First create a patient and an appointment
    patient_id = create_test_patient(client)
    
    # Create appointment data
    appointment_data = TEST_APPOINTMENT.copy()
    appointment_data["patient_id"] = patient_id
    
    # Create the appointment
    create_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = create_response.json()["id"]
    
    # Update the appointment
    update_data = {
        "status": "completed",
        "description": "Appointment completed successfully"
    }
    
    response = client.put(f"/api/appointments/{appointment_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == appointment_id
    assert data["status"] == "completed"
    assert data["description"] == "Appointment completed successfully"
    # After update, updated_at should be set
    assert data.get("updated_at") is not None

def test_delete_appointment(client):
    """Test deleting an appointment"""
    # First create a patient and an appointment
    patient_id = create_test_patient(client)
    
    # Create appointment data
    appointment_data = TEST_APPOINTMENT.copy()
    appointment_data["patient_id"] = patient_id
    
    # Create the appointment
    create_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = create_response.json()["id"]
    
    # Delete the appointment (soft delete)
    response = client.delete(f"/api/appointments/{appointment_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data.get("status") == "success"
    
    # Verify the appointment status is updated to 'cancelled'
    response = client.get(f"/api/appointments/{appointment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"
    assert data.get("updated_at") is not None  # Should be updated

def test_get_appointments_list(client):
    """Test retrieving a list of appointments"""
    # First create a patient
    patient_id = create_test_patient(client)
    
    # Create two test appointments
    for i in range(2):
        appointment_data = TEST_APPOINTMENT.copy()
        appointment_data["patient_id"] = patient_id
        appointment_data["appointment_date"] = get_future_date(i + 1)
        client.post("/api/appointments/", json=appointment_data)
    
    # Get the list of appointments
    response = client.get("/api/appointments/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all(appt["patient_id"] == patient_id for appt in data)
    # Verify each appointment has the expected fields
    for appt in data:
        assert "id" in appt
        assert "created_at" in appt
        # updated_at might be None for newly created records
        assert appt.get("updated_at") is None or isinstance(appt["updated_at"], str)
