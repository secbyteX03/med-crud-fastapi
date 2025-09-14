from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, database

router = APIRouter()

@router.post("/", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(database.get_db)):
    # Check if patient exists
    db_patient = crud.get_patient(db, patient_id=appointment.patient_id)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {appointment.patient_id} not found"
        )
    return crud.create_appointment(db=db, appointment=appointment)

@router.get("/", response_model=List[schemas.Appointment])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    appointments = crud.get_appointments(db, skip=skip, limit=limit)
    return appointments

@router.get("/{appointment_id}", response_model=schemas.Appointment)
def read_appointment(appointment_id: int, db: Session = Depends(database.get_db)):
    db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@router.put("/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int, 
    appointment: schemas.AppointmentUpdate, 
    db: Session = Depends(database.get_db)
):
    db_appointment = crud.update_appointment(db, appointment_id=appointment_id, appointment=appointment)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_200_OK)
def delete_appointment(appointment_id: int, db: Session = Depends(database.get_db)):
    db_appointment = crud.delete_appointment(db, appointment_id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"status": "success", "message": "Appointment cancelled successfully"}
