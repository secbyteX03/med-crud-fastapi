# 🏥 Clinic Management API

<div align="center">
  <h1> Clinic Management API</h1>
  <p>
    <em>A modern, robust, and scalable FastAPI-based solution for managing medical clinic operations</em>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/FastAPI-0.100.0-green.svg" alt="FastAPI Version">
    <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
    <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status">
  </p>
  <img src="screenshots/banner.png" alt="Clinic Management API" style="max-width: 100%; border-radius: 8px; margin: 20px 0;">
</div>

## Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Using the API](#-using-the-api)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## Features

- **Comprehensive Patient Management** - Full CRUD operations for patient records
- **Efficient Appointment System** - Schedule, update, and track appointments
- **Modern Tech Stack** - Built with FastAPI, SQLAlchemy, and Pydantic
- **Production-Ready** - Includes error handling, validation, and logging
- **RESTful Design** - Intuitive API endpoints following best practices
- **Multiple Database Support** - SQLite (default) or MySQL compatible
- **Secure** - Environment-based configuration and sensitive data protection

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- (Optional) MySQL 8.0+ if not using SQLite

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/secbyteX03/med-crud-fastapi.git
   cd med-crud-fastapi
   ```

2. **Set up a virtual environment**
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
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Database configuration (SQLite default)
   DATABASE_URL=sqlite:///./clinic.db
   
   # For MySQL:
   # DATABASE_URL=mysql+pymysql://user:password@localhost/clinic_db
   
   # Security settings
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access API documentation**
   - Interactive API docs: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc

## Using the API

### Interactive Documentation

![API Documentation](screenshots/api_docs.png)

Visit http://127.0.0.1:8000/docs to explore and test all API endpoints directly from your browser.

### cURL Examples

**Get All Patients**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/patients/' -H 'accept: application/json'
```

**Create a New Patient**
```bash
curl -X 'POST' 'http://127.0.0.1:8000/patients/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "phone_number": "+254738465738",
    "email": "john.doe@example.com",
    "address": "123 Main St"
  }'
```

### Python Example
```python
import requests
import json

# Get all patients
response = requests.get('http://127.0.0.1:8000/patients/')
print("Patients:", response.json())

# Create new patient
new_patient = {
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1985-05-20",
    "gender": "female",
    "phone_number": "+254738465744",
    "email": "jane.smith@example.com",
    "address": "456 Oak St"
}

response = requests.post(
    'http://127.0.0.1:8000/patients/',
    headers={"Content-Type": "application/json"},
    data=json.dumps(new_patient)
)
print("New Patient:", response.json())
```

### Postman Example

![Postman Example](screenshots/postman.png)

## API Endpoints

### Patients

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/patients/` | Get all patients | - |
| `GET` | `/patients/{id}` | Get specific patient | Patient ID |
| `POST` | `/patients/` | Create new patient | Patient data |
| `PUT` | `/patients/{id}` | Update patient | Patient ID, Updated data |
| `DELETE` | `/patients/{id}` | Delete patient | Patient ID |

### Appointments

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/appointments/` | Get all appointments | - |
| `GET` | `/appointments/{id}` | Get specific appointment | Appointment ID |
| `POST` | `/appointments/` | Create new appointment | Appointment data |
| `PUT` | `/appointments/{id}` | Update appointment | Appointment ID, Updated data |
| `DELETE` | `/appointments/{id}` | Cancel appointment | Appointment ID |

## 🧪 Testing

The application includes a comprehensive test suite to ensure reliability and prevent regressions. The tests are written using `pytest` and include both unit and integration tests.

### Test Structure

```
app/tests/
├── __init__.py
├── test_patients.py    # Tests for patient endpoints
└── test_appointments.py # Tests for appointment endpoints
```

Test fixtures and configurations are included directly in the test files.

### Running Tests

To run the test suite, use the following command:

```bash
pytest app/tests/ -v
```

### Test Coverage

The test suite covers:

1. **Patient Endpoints**
   - Creating new patients
   - Retrieving patient details
   - Updating patient information
   - Deleting patients
   - Error handling for invalid requests

2. **Appointment Endpoints**
   - Scheduling new appointments
   - Retrieving appointment details
   - Updating appointments
   - Cancelling appointments (soft delete)
   - Error handling for invalid requests
   - Validation of appointment dates and statuses

### Test Database

- Tests use a separate SQLite database (`test_clinic.db`) to avoid affecting development data
- The test database is automatically created and destroyed with each test run
- All database operations are rolled back after each test to ensure test isolation

### Fixtures

Key test fixtures include:
- `test_db`: Sets up and tears down the test database
- `client`: Provides a test client for making HTTP requests
- Test data factories for creating consistent test data

### Recent Test Improvements

- Fixed issues with database session management in tests
- Added comprehensive error handling tests
- Improved test isolation and reliability
- Added validation for response schemas
- Implemented proper cleanup of test data

## 📁 Project Structure

```
med-crud-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   └── routers/             # API routes
│       ├── __init__.py
│       ├── patients.py      # Patient endpoints
│       └── appointments.py  # Appointment endpoints
├── tests/                   # Test suite
├── .env                    # Environment variables
├── .env.example            # Example environment variables
├── requirements.txt        # Python dependencies
├── init_db.py             # Database initialization
└── README.md              # Project documentation
```

## 🧪 Testing

Run the test suite with pytest:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <p>Made by the Clinic Management API Team</p>
</div>