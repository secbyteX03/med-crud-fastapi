import logging
import sys
from fastapi import FastAPI, Request, status, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import traceback
from typing import Callable, Any, Dict, Optional
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from .routers import patients, appointments
from .config import settings
from .database import Base, engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import inspect

# Configure logging to ensure all output goes to console and file
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format)

# Get the root logger and set level to DEBUG
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Remove all existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Create console handler with debug level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_formatter)

# Create file handler which logs even debug messages
file_handler = logging.FileHandler('app.log', mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)

# Add the handlers to the root logger
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Configure uvicorn logger
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = []
uvicorn_logger.propagate = True
uvicorn_logger.setLevel(logging.DEBUG)
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.handlers = []
uvicorn_access.propagate = True
uvicorn_access.setLevel(logging.DEBUG)

# Configure SQLAlchemy logger
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging.INFO)
sqlalchemy_logger.handlers = []
sqlalchemy_logger.propagate = True

# Get logger for this module
logger = logging.getLogger(__name__)
logger.debug("Logging configuration complete")

# Custom exception handler for unhandled exceptions
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the full error with traceback
    logger.error("Unhandled exception occurred:", exc_info=exc)
    
    # Get detailed error information
    error_detail = {
        "error": str(exc),
        "type": exc.__class__.__name__,
        "path": request.url.path,
        "method": request.method
    }
    
    # Log the error details
    logger.error(f"Error details: {error_detail}")
    
    # Return a JSON response with the error details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# Custom middleware to log all requests and responses
async def log_requests(request: Request, call_next: Callable) -> Response:
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Log response
        logger.info(f"Response: {response.status_code}")
        return response
        
    except Exception as exc:
        # Log any unhandled exceptions
        logger.error("Unhandled exception in request:", exc_info=exc)
        # Re-raise to let the global exception handler handle it
        raise

# Create FastAPI app
app = FastAPI(
    title="Clinic Management API",
    description="API for managing patients and appointments in a clinic",
    version="1.0.0",
    debug=True
)

# Initialize database tables
@app.on_event("startup")
def on_startup():
    logger.info("Creating database tables if they don't exist...")
    try:
        # Create all tables defined in Base.metadata
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Verify tables were created
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        logger.info(f"Available tables: {table_names}")
        
        # If no patients exist, add a test patient
        with Session(engine) as db:
            from app.models import Patient
            patient_count = db.query(Patient).count()
            logger.info(f"Found {patient_count} patients in the database")
            
            if patient_count == 0:
                logger.info("Adding a test patient to the database...")
                test_patient = Patient(
                    first_name="Test",
                    last_name="Patient",
                    date_of_birth="1990-01-01",
                    gender="Other",
                    phone_number="+254712345678",
                    email="test@example.com",
                    address="123 Test St, Nairobi, Kenya"
                )
                db.add(test_patient)
                db.commit()
                logger.info("Added test patient to the database")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

# Add exception handlers
# Note: HTTPException is handled by FastAPI by default, no need to add it here
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(ValidationError, global_exception_handler)

# Add request/response logging middleware
app.middleware('http')(log_requests)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Clinic Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
