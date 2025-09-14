import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, database, models

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add stream handler to ensure logs are visible in console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

router = APIRouter()

@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(database.get_db)):
    return crud.create_patient(db=db, patient=patient)

@router.get("/", response_model=List[schemas.Patient])
async def read_patients(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db)
):
    logger.info(f"=== Starting GET /api/patients with skip={skip}, limit={limit} ===")
    
    try:
        # Log request details
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Get patients from database
        logger.info("Calling crud.get_patients()")
        patients = crud.get_patients(db, skip=skip, limit=limit)
        logger.info(f"Retrieved {len(patients)} patients from database")
        
        # Log sample patient data (first 2 patients)
        for i, patient in enumerate(patients[:2]):
            logger.debug(f"Patient {i+1}: ID={patient.id}, Name={patient.first_name} {patient.last_name}")
        if len(patients) > 2:
            logger.debug(f"... and {len(patients) - 2} more patients")
            
        logger.info("=== Successfully processed GET /api/patients ===")
        return patients
        
    except Exception as e:
        # Log detailed error information
        logger.error("=== ERROR in GET /api/patients ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        
        # Log database state for debugging
        try:
            logger.info("Attempting to check database connection and tables...")
            # Try a simple query to check database connection
            db.execute("SELECT 1")
            logger.info("Database connection test query succeeded")
            
            # Check if patients table exists
            if db.bind.dialect.has_table(db.bind, 'patients'):
                logger.info("Patients table exists")
                # Try to count patients
                count = db.query(models.Patient).count()
                logger.info(f"Found {count} patients in database")
            else:
                logger.error("Patients table does not exist!")
                
        except Exception as db_error:
            logger.error("Error checking database state:", exc_info=True)
        
        # Re-raise with more detailed error message
        error_detail = f"An error occurred while fetching patients: {str(e)}"
        logger.error(f"Raising HTTP 500 with detail: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(database.get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int, 
    patient: schemas.PatientUpdate, 
    db: Session = Depends(database.get_db)
):
    db_patient = crud.update_patient(db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_patient(db, patient_id=patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"ok": True}
