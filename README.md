<div align="center">
  <h1>🏥 Clinic Management API</h1>
  <p>
    <em>A modern, robust, and scalable FastAPI-based solution for managing medical clinic operations</em>
  </p>
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-endpoints">API Endpoints</a> •
    <a href="#testing">Testing</a> •
    <a href="#database-schema">Database Schema</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/FastAPI-0.100.0-green.svg" alt="FastAPI Version">
    <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  </p>
</div>

## 🌟 Features

- **Comprehensive Patient Management** - Full CRUD operations for patient records
- **Efficient Appointment System** - Schedule, update, and track appointments
- **Modern Tech Stack** - Built with FastAPI, SQLAlchemy, and Pydantic
- **Production-Ready** - Includes error handling, validation, and logging
- **RESTful Design** - Intuitive API endpoints following best practices
- **Multiple Database Support** - SQLite (default) or MySQL compatible
- **Secure** - Environment-based configuration and sensitive data protection

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) MySQL 8.0+ if not using SQLite

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/secbyteX03/med-crud-fastapi.git
   cd med-crud-fastapi
   ```

2. **Set up a virtual environment** (highly recommended)
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   copy .env.example .env  # Windows
   cp .env.example .env    # macOS/Linux
   ```
   
   Update the `.env` file with your configuration:
   ```env
   # Database configuration (SQLite default)
   DATABASE_URL=sqlite:///./clinic.db
   
   # For MySQL, use:
   # DATABASE_URL=mysql+pymysql://user:password@localhost/clinic_db
   
   # Security settings
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Initialize the database**
   ```bash
   # For SQLite (default)
   python init_db.py
   
   # For MySQL, ensure the database exists first, then run:
   # python init_db.py
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the API documentation**
   - Interactive API docs: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc

## 🖥️ Using the API

After starting the application, you can interact with the API in several ways:

### 1. Using the Interactive API Documentation
1. Open your web browser and go to: http://127.0.0.1:8000/docs
2. You'll see all available API endpoints organized by category (Patients and Appointments)
3. Click on any endpoint to expand it
4. Click the "Try it out" button to test the endpoint directly from your browser
5. Fill in any required parameters and click "Execute" to see the response

### 2. Using cURL (Command Line)

**Example: Get All Patients**
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/patients/' \
  -H 'accept: application/json'
```

**Example: Create a New Patient**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/patients/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "phone_number": "1234567890",
    "email": "john.doe@example.com",
    "address": "123 Main St"
  }'
```

### 3. Using Postman
1. Import the provided `postman_collection.json` file into Postman
2. You'll find pre-configured requests for all API endpoints
3. Click on any request to send it to the API

### 4. Programmatic Access (Python Example)

```python
import requests
import json

# Get all patients
response = requests.get('http://127.0.0.1:8000/patients/')
print("All Patients:", response.json())

# Create a new patient
new_patient = {
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1985-05-15",
    "gender": "female",
    "phone_number": "0987654321",
    "email": "jane.smith@example.com",
    "address": "456 Oak St"
}

response = requests.post(
    'http://127.0.0.1:8000/patients/',
    headers={"Content-Type": "application/json"},
    data=json.dumps(new_patient)
)
print("New Patient Created:", response.json())
```

## 🔌 API Endpoints

### Patients

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/patients/` | Get all patients |
| `GET` | `/patients/{id}` | Get a specific patient |
| `POST` | `/patients/` | Create a new patient |
| `PUT` | `/patients/{id}` | Update a patient |
| `DELETE` | `/patients/{id}` | Delete a patient |

### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/appointments/` | Get all appointments |
| `GET` | `/appointments/{id}` | Get a specific appointment |
| `POST` | `/appointments/` | Create a new appointment |
| `PUT` | `/appointments/{id}` | Update an appointment |
| `DELETE` | `/appointments/{id}` | Cancel an appointment (soft delete) |

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-cov

# Run all tests
pytest

# Run specific test file
pytest tests/test_patients.py
```

## 🛠 Project Structure

```
med-crud-fastapi/
├── app/                      # Application package
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration settings
│   ├── database.py           # Database connection
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── crud.py               # Database operations
│   └── routers/              # API routes
│       ├── __init__.py
│       ├── patients.py       # Patient endpoints
│       └── appointments.py   # Appointment endpoints
├── tests/                    # Test files
├── .env.example              # Example environment variables
├── requirements.txt          # Project dependencies
├── init_db.py               # Database initialization
└── README.md                # This file
```

## 📝 Example Requests

### Create a New Patient
```bash
curl -X 'POST' \
  'http://localhost:8000/api/patients' \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1985-05-15",
    "gender": "Male",
    "phone_number": "+254723242435",
    "email": "john.doe@example.com",
    "address": "123 Moi Avenue, Nairobi"
  }'
```

### Schedule an Appointment
```bash
curl -X 'POST' \
  'http://localhost:8000/api/appointments' \
  -H 'Content-Type: application/json' \
  -d '{
    "patient_id": 1,
    "appointment_date": "2025-10-01T09:00:00",
    "description": "Annual checkup"
  }'
```

## 👏 Acknowledgments

- FastAPI for the amazing framework
- SQLAlchemy for ORM support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
- [x] Requirements file with all dependencies

## License

This project is licensed under the MIT License.
