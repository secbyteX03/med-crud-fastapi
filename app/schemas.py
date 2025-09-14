from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

# Patient schemas
class PatientBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    date_of_birth: date
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None

class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Appointment schemas
class AppointmentBase(BaseModel):
    patient_id: int
    appointment_date: datetime
    description: Optional[str] = None
    status: Optional[str] = "scheduled"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Appointment(AppointmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient: Optional[Patient] = None

    class Config:
        from_attributes = True

# Response models
class ResponseModel(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
