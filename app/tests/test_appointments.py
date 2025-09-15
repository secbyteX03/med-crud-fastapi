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

# Create a temporary SQLite database file for testing
import tempfile
import os

# Create a temporary file for the test database
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db_path = temp_db.name
temp_db.close()

# Set up the database URL for SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db_path}"

# Create engine with a single connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

# Clean up the temporary database file after tests
import atexit
import os

def cleanup():
    try:
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
    except Exception as e:
        print(f"Error cleaning up test database: {e}")

atexit.register(cleanup)

# Function to get a database session for the app
def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency in the FastAPI app
app.dependency_overrides[get_db] = get_test_db

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

# Fixture to create a test database with proper isolation
@pytest.fixture(scope="function")
def test_db():
    # Drop all tables and recreate them to ensure a clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        # Clean up
        db.rollback()
        db.close()

# Fixture to get a test client with proper isolation
@pytest.fixture
def client(test_db):
    # Use the test_db session for the client
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the dependency overrides
    app.dependency_overrides.clear()

# Helper function to create a test patient
def create_test_patient(client):
    response = client.post("/api/patients/", json=TEST_PATIENT)
    assert response.status_code == 201, f"Failed to create test patient: {response.text}"
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
    # Write debug output to a file
    with open('test_debug.log', 'w') as f:
        f.write("=== Starting test_get_appointments_list ===\n\n")
        
        # First create a patient
        f.write("=== Creating test patient ===\n")
        patient_response = client.post("/api/patients/", json=TEST_PATIENT)
        patient_data = patient_response.json()
        patient_id = patient_data["id"]
        f.write(f"Created patient with ID: {patient_id}\n")
        f.write(f"Patient creation status: {patient_response.status_code}\n")
        f.write(f"Patient creation response: {patient_response.text}\n\n")
        
        # Verify patient was created
        patient_get = client.get(f"/api/patients/{patient_id}")
        f.write(f"Patient get status: {patient_get.status_code}\n")
        f.write(f"Patient data: {patient_get.text}\n\n")
        
        # Create two test appointments
        appointment_ids = []
        for i in range(2):
            f.write(f"\n=== Creating test appointment {i+1} ===\n")
            appointment_data = TEST_APPOINTMENT.copy()
            appointment_data["patient_id"] = patient_id
            appointment_data["appointment_date"] = get_future_date(i + 1)
            f.write(f"Sending appointment data: {appointment_data}\n")
            
            response = client.post("/api/appointments/", json=appointment_data)
            f.write(f"Appointment {i+1} creation status: {response.status_code}\n")
            f.write(f"Appointment {i+1} creation response: {response.text}\n")
            
            if response.status_code == 201:
                appt_data = response.json()
                appointment_ids.append(appt_data["id"])
                f.write(f"Created appointment {i+1} with ID: {appt_data['id']}\n")
                
                # Verify appointment was created
                appt_get = client.get(f"/api/appointments/{appt_data['id']}")
                f.write(f"Appointment {i+1} get status: {appt_get.status_code}\n")
                f.write(f"Appointment {i+1} data: {appt_get.text}\n")
        
        # Get the list of appointments
        f.write("\n=== Getting list of appointments ===\n")
        response = client.get("/api/appointments/")
        f.write(f"Get appointments list status: {response.status_code}\n")
        f.write(f"Response content: {response.text}\n")
        
        # Verify the response
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
        
        data = response.json()
        f.write(f"\nParsed data type: {type(data)}\n")
        f.write(f"Number of appointments: {len(data)}\n")
        
        assert isinstance(data, list), f"Expected a list but got {type(data)}"
        assert len(data) == 2, f"Expected 2 appointments but got {len(data)}. Data: {data}"
        
        # Write each appointment to the debug file
        f.write("\n=== Appointments in response ===\n")
        for i, appt in enumerate(data):
            f.write(f"Appointment {i+1}: {appt}\n")
            
            # Verify each appointment has the expected fields
            required_fields = ["id", "patient_id", "appointment_date", "status", "description", "created_at"]
            for field in required_fields:
                assert field in appt, f"Appointment {i+1} missing required field: {field}"
            
            # Verify patient_id matches
            assert appt["patient_id"] == patient_id, f"Appointment {i+1} has wrong patient_id: {appt['patient_id']} (expected {patient_id})"
            
            # Verify updated_at is either None or a string
            assert appt.get("updated_at") is None or isinstance(appt["updated_at"], str), \
                f"Appointment {i+1} has invalid 'updated_at' field: {appt.get('updated_at')}"
        
        f.write("\n=== test_get_appointments_list completed successfully ===\n")
