"""
Database Management System
Handles SQLAlchemy ORM initialization, sessions, and CRUD operations
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from contextlib import contextmanager
from config import DATABASE_URL, DEBUG_MODE
from database_models import Base, Patient, Analysis, MedicalReport, DietPlan, Recommendation, Appointment

logger = logging.getLogger(__name__)

# ========================
# DATABASE INITIALIZATION
# ========================

# SQLite database configuration (optimal for local development/deployment)
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=DEBUG_MODE
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        echo=DEBUG_MODE,
        pool_pre_ping=True
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def drop_db():
    """Drop all tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("⚠️  All database tables dropped")
    except Exception as e:
        logger.error(f"❌ Database drop failed: {e}")
        raise

# ========================
# SESSION MANAGEMENT
# ========================

def get_db():
    """Get database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================
# PATIENT CRUD OPERATIONS
# ========================

class PatientDB:
    """Patient database operations"""
    
    @staticmethod
    def create(db: Session, patient_id: str, name: str, age: int, sex: str, 
               location: str, email: str = None, phone: str = None, 
               medical_history: str = None, allergies: list = None) -> Patient:
        """Create new patient record"""
        try:
            patient = Patient(
                id=patient_id,
                name=name,
                age=age,
                sex=sex,
                location=location,
                email=email,
                phone=phone,
                medical_history=medical_history,
                allergies=allergies
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            logger.info(f"✅ Patient created: {patient_id}")
            return patient
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create patient: {e}")
            raise

    @staticmethod
    def get(db: Session, patient_id: str) -> Patient:
        """Get patient by ID"""
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            return patient
        except Exception as e:
            logger.error(f"❌ Failed to get patient: {e}")
            return None

    @staticmethod
    def get_by_email(db: Session, email: str) -> Patient:
        """Get patient by email"""
        try:
            patient = db.query(Patient).filter(Patient.email == email).first()
            return patient
        except Exception as e:
            logger.error(f"❌ Failed to get patient by email: {e}")
            return None

    @staticmethod
    def list_all(db: Session, limit: int = 100, offset: int = 0) -> list:
        """List all patients"""
        try:
            patients = db.query(Patient).limit(limit).offset(offset).all()
            return patients
        except Exception as e:
            logger.error(f"❌ Failed to list patients: {e}")
            return []

    @staticmethod
    def update(db: Session, patient_id: str, **kwargs) -> Patient:
        """Update patient record"""
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                for key, value in kwargs.items():
                    if hasattr(patient, key):
                        setattr(patient, key, value)
                db.commit()
                db.refresh(patient)
                logger.info(f"✅ Patient updated: {patient_id}")
            return patient
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update patient: {e}")
            raise

    @staticmethod
    def delete(db: Session, patient_id: str) -> bool:
        """Delete patient record"""
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                db.delete(patient)
                db.commit()
                logger.info(f"✅ Patient deleted: {patient_id}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to delete patient: {e}")
            raise

# ========================
# ANALYSIS CRUD OPERATIONS
# ========================

class AnalysisDB:
    """Analysis database operations"""
    
    @staticmethod
    def create(db: Session, analysis_id: str, patient_id: str = None, 
               eye_image_path: str = None, nails_image_path: str = None, 
               tongue_image_path: str = None) -> Analysis:
        """Create new analysis record"""
        try:
            analysis = Analysis(
                id=analysis_id,
                patient_id=patient_id,
                eye_image_path=eye_image_path,
                nails_image_path=nails_image_path,
                tongue_image_path=tongue_image_path,
                status="pending"
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            logger.info(f"✅ Analysis created: {analysis_id}")
            return analysis
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create analysis: {e}")
            raise

    @staticmethod
    def get(db: Session, analysis_id: str) -> Analysis:
        """Get analysis by ID"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            return analysis
        except Exception as e:
            logger.error(f"❌ Failed to get analysis: {e}")
            return None

    @staticmethod
    def get_patient_analyses(db: Session, patient_id: str) -> list:
        """Get all analyses for a patient"""
        try:
            analyses = db.query(Analysis).filter(Analysis.patient_id == patient_id).all()
            return analyses
        except Exception as e:
            logger.error(f"❌ Failed to get patient analyses: {e}")
            return []

    @staticmethod
    def update(db: Session, analysis_id: str, **kwargs) -> Analysis:
        """Update analysis record"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                for key, value in kwargs.items():
                    if hasattr(analysis, key):
                        setattr(analysis, key, value)
                db.commit()
                db.refresh(analysis)
                logger.info(f"✅ Analysis updated: {analysis_id}")
            return analysis
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update analysis: {e}")
            raise

    @staticmethod
    def update_status(db: Session, analysis_id: str, status: str, 
                     processing_time: float = None, error_message: str = None) -> Analysis:
        """Update analysis status"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = status
                if processing_time:
                    analysis.processing_time_seconds = processing_time
                if error_message:
                    analysis.error_message = error_message
                db.commit()
                db.refresh(analysis)
                logger.info(f"✅ Analysis status updated: {analysis_id} -> {status}")
            return analysis
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update analysis status: {e}")
            raise

    @staticmethod
    def delete(db: Session, analysis_id: str) -> bool:
        """Delete analysis record"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                db.delete(analysis)
                db.commit()
                logger.info(f"✅ Analysis deleted: {analysis_id}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to delete analysis: {e}")
            raise

# ========================
# REPORT CRUD OPERATIONS
# ========================

class ReportDB:
    """Medical report database operations"""
    
    @staticmethod
    def create(db: Session, report_id: str, analysis_id: str, 
               report_text: str = None, report_file_path: str = None,
               assessment: str = None, severity: str = None) -> MedicalReport:
        """Create medical report"""
        try:
            report = MedicalReport(
                id=report_id,
                analysis_id=analysis_id,
                report_text=report_text,
                report_file_path=report_file_path,
                assessment=assessment,
                severity=severity
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            logger.info(f"✅ Report created: {report_id}")
            return report
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create report: {e}")
            raise

    @staticmethod
    def get_by_analysis(db: Session, analysis_id: str) -> MedicalReport:
        """Get report by analysis ID"""
        try:
            report = db.query(MedicalReport).filter(
                MedicalReport.analysis_id == analysis_id
            ).first()
            return report
        except Exception as e:
            logger.error(f"❌ Failed to get report: {e}")
            return None

# ========================
# APPOINTMENT CRUD OPERATIONS
# ========================

class AppointmentDB:
    """Appointment database operations"""
    
    @staticmethod
    def create(db: Session, appointment_id: str, patient_id: str,
               doctor_name: str, specialty: str, appointment_time: str,
               status: str = "scheduled") -> Appointment:
        """Create appointment"""
        try:
            appointment = Appointment(
                id=appointment_id,
                patient_id=patient_id,
                doctor_name=doctor_name,
                specialty=specialty,
                appointment_time=appointment_time,
                status=status
            )
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            logger.info(f"✅ Appointment created: {appointment_id}")
            return appointment
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create appointment: {e}")
            raise

    @staticmethod
    def get_patient_appointments(db: Session, patient_id: str) -> list:
        """Get all appointments for patient"""
        try:
            appointments = db.query(Appointment).filter(
                Appointment.patient_id == patient_id
            ).all()
            return appointments
        except Exception as e:
            logger.error(f"❌ Failed to get appointments: {e}")
            return []

# ========================
# DATABASE STATISTICS
# ========================

class DatabaseStats:
    """Get database statistics"""
    
    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get overall database statistics"""
        try:
            total_patients = db.query(Patient).count()
            total_analyses = db.query(Analysis).count()
            completed_analyses = db.query(Analysis).filter(
                Analysis.status == "completed"
            ).count()
            total_reports = db.query(MedicalReport).count()
            total_appointments = db.query(Appointment).count()
            
            return {
                "total_patients": total_patients,
                "total_analyses": total_analyses,
                "completed_analyses": completed_analyses,
                "pending_analyses": total_analyses - completed_analyses,
                "total_reports": total_reports,
                "total_appointments": total_appointments
            }
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized!")
