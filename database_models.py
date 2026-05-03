"""
Database Models for Patient and Analysis History
Using SQLAlchemy ORM (optional integration)
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config import DATABASE_URL

Base = declarative_base()


class Patient(Base):
    """Patient demographic information"""
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(String, nullable=True)
    location = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    phone = Column(String, nullable=True)
    medical_history = Column(Text, nullable=True)
    allergies = Column(JSON, nullable=True)
    medications = Column(JSON, nullable=True)
    dietary_preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.name})>"


class Analysis(Base):
    """Medical analysis record"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=True)
    
    # Image metadata
    eye_image_path = Column(String, nullable=True)
    nails_image_path = Column(String, nullable=True)
    tongue_image_path = Column(String, nullable=True)
    
    # Analysis results
    eye_analysis = Column(Text, nullable=True)
    nails_analysis = Column(Text, nullable=True)
    tongue_analysis = Column(Text, nullable=True)
    comprehensive_diagnosis = Column(Text, nullable=True)
    
    # Confidence scores
    eye_confidence = Column(Float, default=0.0)
    nails_confidence = Column(Float, default=0.0)
    tongue_confidence = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, error
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="analyses")
    report = relationship("MedicalReport", back_populates="analysis", uselist=False)
    diet_plan = relationship("DietPlan", back_populates="analysis", uselist=False)
    recommendations = relationship("Recommendation", back_populates="analysis")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, patient_id={self.patient_id}, status={self.status})>"


class MedicalReport(Base):
    """Generated medical report"""
    __tablename__ = "medical_reports"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    
    report_text = Column(Text, nullable=True)
    report_file_path = Column(String, nullable=True)
    
    # Report details
    assessment = Column(String, nullable=True)  # Normal/At Risk/Abnormal
    severity = Column(String, nullable=True)     # None/Mild/Moderate/Severe
    
    # Follow-up
    requires_followup = Column(String, default="No")
    recommended_specialist = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="report")
    
    def __repr__(self):
        return f"<MedicalReport(id={self.id}, analysis_id={self.analysis_id})>"


class DietPlan(Base):
    """Generated diet plan"""
    __tablename__ = "diet_plans"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    
    plan_text = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    
    # Plan details
    duration_days = Column(Integer, default=30)
    severity_level = Column(String, nullable=True)  # mild, moderate, severe
    
    # Recommendations
    vitamins_minerals = Column(JSON, nullable=True)
    proteins = Column(JSON, nullable=True)
    carbohydrates = Column(JSON, nullable=True)
    healthy_fats = Column(JSON, nullable=True)
    foods_to_avoid = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="diet_plan")
    
    def __repr__(self):
        return f"<DietPlan(id={self.id}, analysis_id={self.analysis_id})>"


class Recommendation(Base):
    """Healthcare provider recommendations"""
    __tablename__ = "recommendations"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    
    # Provider info
    provider_name = Column(String, nullable=True)
    provider_type = Column(String, nullable=True)  # Doctor/Hospital
    specialty = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Recommendation details
    reason = Column(Text, nullable=True)
    match_score = Column(Float, default=0.0)
    contact_info = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, provider={self.provider_name})>"


class Appointment(Base):
    """Appointment booking"""
    __tablename__ = "appointments"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    
    # Appointment details
    doctor_name = Column(String, nullable=True)
    hospital_name = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    appointment_date = Column(DateTime, nullable=True)
    appointment_time = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="scheduled")  # scheduled, confirmed, cancelled, completed
    notes = Column(Text, nullable=True)
    
    # Reminders
    reminder_sent = Column(String, default="No")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    patient = relationship("Patient", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, status={self.status})>"


class AnalysisHistory(Base):
    """Analysis tracking for analytics"""
    __tablename__ = "analysis_history"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Event
    event_type = Column(String)  # image_upload, analysis_started, analysis_completed, report_generated, etc
    event_data = Column(JSON, nullable=True)
    
    # Performance
    duration_ms = Column(Float, nullable=True)


# Database initialization
def init_db(database_url: str = DATABASE_URL):
    """Initialize database"""
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine


def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()


# Repository functions for database operations

class PatientRepository:
    """Patient data access"""
    
    @staticmethod
    def create(session, **kwargs) -> Patient:
        patient = Patient(**kwargs)
        session.add(patient)
        session.commit()
        return patient
    
    @staticmethod
    def get_by_id(session, patient_id: str) -> Optional[Patient]:
        return session.query(Patient).filter(Patient.id == patient_id).first()
    
    @staticmethod
    def get_by_email(session, email: str) -> Optional[Patient]:
        return session.query(Patient).filter(Patient.email == email).first()
    
    @staticmethod
    def list_all(session, limit: int = 100, offset: int = 0) -> List[Patient]:
        return session.query(Patient).limit(limit).offset(offset).all()
    
    @staticmethod
    def update(session, patient_id: str, **kwargs) -> Optional[Patient]:
        patient = PatientRepository.get_by_id(session, patient_id)
        if patient:
            for key, value in kwargs.items():
                setattr(patient, key, value)
            session.commit()
        return patient


class AnalysisRepository:
    """Analysis data access"""
    
    @staticmethod
    def create(session, **kwargs) -> Analysis:
        analysis = Analysis(**kwargs)
        session.add(analysis)
        session.commit()
        return analysis
    
    @staticmethod
    def get_by_id(session, analysis_id: str) -> Optional[Analysis]:
        return session.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    @staticmethod
    def get_by_patient(session, patient_id: str) -> List[Analysis]:
        return session.query(Analysis).filter(Analysis.patient_id == patient_id).all()
    
    @staticmethod
    def list_recent(session, limit: int = 10) -> List[Analysis]:
        return session.query(Analysis).order_by(Analysis.created_at.desc()).limit(limit).all()


# Usage example
if __name__ == "__main__":
    # Initialize database
    engine = init_db()
    session = get_session(engine)
    
    # Create patient
    patient = PatientRepository.create(
        session,
        id="PAT001",
        name="John Doe",
        age=35,
        sex="Male",
        email="john@example.com"
    )
    
    print(f"Created: {patient}")
    
    # Close session
    session.close()
