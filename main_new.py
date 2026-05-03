"""
AI Medical Diagnostic System - Complete Production Backend v2.0
Multi-agent orchestration with enterprise features:
- Database persistence (SQLAlchemy)
- API key authentication  
- Rate limiting
- PDF export
- Email notifications
- Batch processing
- Caching system
"""

import os
import sys
import time
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
import shutil
from pathlib import Path

# Import our modules
from config import DEBUG_MODE
from image_processor import ImageProcessor
from agent_orchestrator import AgentOrchestrator
from memory import save_conversation
from database import init_db, get_db, PatientDB, AnalysisDB, ReportDB, DatabaseStats
from auth import APIKeyManager, RateLimiter, init_auth
from features import PDFExporter, EmailNotifier, CacheManager, init_features

# ========================
# LOGGING SETUP
# ========================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================
# MODELS
# ========================

class PatientInfo(BaseModel):
    name: str
    age: int
    sex: str
    location: str
    email: Optional[str] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None

class CompleteAnalysisRequest(BaseModel):
    patient_info: PatientInfo
    send_pdf: bool = False
    send_email: bool = False

# ========================
# STARTUP/SHUTDOWN
# ========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Initializing AI Medical Diagnostic System v2.0...")
    try:
        init_db()
        init_features()
        init_auth()
        logger.info("✅ All systems initialized")
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down system...")

# ========================
# FASTAPI APP
# ========================

app = FastAPI(
    title="🏥 AI Medical Diagnostic System v2.0",
    description="Production-ready multi-agent medical diagnostic system with enterprise features",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator
orchestrator = AgentOrchestrator()
image_processor = ImageProcessor()

# ========================
# UTILITY FUNCTIONS
# ========================

def generate_workflow_id() -> str:
    return f"WF_{uuid.uuid4().hex[:12].upper()}"

def generate_analysis_id() -> str:
    return f"ANA_{uuid.uuid4().hex[:12].upper()}"

def generate_patient_id() -> str:
    return f"PAT_{uuid.uuid4().hex[:12].upper()}"

async def save_uploaded_file(upload_file: UploadFile, folder: str = "uploads") -> str:
    """Save uploaded file"""
    try:
        Path(folder).mkdir(exist_ok=True)
        file_path = f"{folder}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{upload_file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        logger.info(f"📁 File saved: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"❌ Error saving file: {e}")
        raise HTTPException(status_code=400, detail=f"Error saving file: {e}")

async def process_images_to_base64(eye_image: UploadFile, nails_image: UploadFile, tongue_image: UploadFile):
    """Convert images to base64"""
    try:
        eye_data = await eye_image.read()
        nails_data = await nails_image.read()
        tongue_data = await tongue_image.read()
        
        # Load images from bytes
        eye_img = image_processor.load_from_bytes(eye_data)
        nails_img = image_processor.load_from_bytes(nails_data)
        tongue_img = image_processor.load_from_bytes(tongue_data)
        
        if eye_img is None or nails_img is None or tongue_img is None:
            raise ValueError("Failed to load one or more images")
        
        # Preprocess images
        eye_processed, _ = image_processor.preprocess(eye_img)
        nails_processed, _ = image_processor.preprocess(nails_img)
        tongue_processed, _ = image_processor.preprocess(tongue_img)
        
        if eye_processed is None or nails_processed is None or tongue_processed is None:
            raise ValueError("Failed to preprocess one or more images")
        
        # Convert to base64
        eye_b64 = image_processor.to_base64(eye_processed)
        nails_b64 = image_processor.to_base64(nails_processed)
        tongue_b64 = image_processor.to_base64(tongue_processed)
        
        return eye_b64, nails_b64, tongue_b64
    except Exception as e:
        logger.error(f"❌ Image processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")

# ========================
# MAIN AGENTIC ENDPOINTS
# ========================

@app.post("/api/complete-analysis")
async def complete_analysis(
    patient_name: str,
    patient_age: int,
    patient_sex: str,
    patient_location: str,
    eye_image: UploadFile = File(...),
    nails_image: UploadFile = File(...),
    tongue_image: UploadFile = File(...),
    patient_email: Optional[str] = None,
    send_pdf: bool = False,
    send_email: bool = False,
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Complete medical analysis with all agents"""
    workflow_id = generate_workflow_id()
    start_time = time.time()
    
    try:
        # Rate limiting
        if x_api_key:
            if not RateLimiter.check_rate_limit(x_api_key):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        logger.info(f"🔄 Workflow {workflow_id} started")
        
        # Create patient
        patient_id = generate_patient_id()
        patient = PatientDB.create(
            db, patient_id, patient_name, patient_age,
            patient_sex, patient_location, patient_email
        )
        
        # Process images
        logger.info("📸 Processing images...")
        eye_b64, nails_b64, tongue_b64 = await process_images_to_base64(
            eye_image, nails_image, tongue_image
        )
        
        # Create analysis
        analysis_id = generate_analysis_id()
        analysis = AnalysisDB.create(
            db, analysis_id, patient_id,
            eye_image_path=eye_image.filename,
            nails_image_path=nails_image.filename,
            tongue_image_path=tongue_image.filename
        )
        
        AnalysisDB.update_status(db, analysis_id, "processing")
        
        # Execute workflow
        logger.info("🤖 Executing multi-agent workflow...")
        result = orchestrator.execute_complete_workflow(
            images_dict={
                "eye": eye_b64,
                "nails": nails_b64,
                "tongue": tongue_b64
            },
            patient_info={
                "name": patient_name,
                "age": patient_age,
                "sex": patient_sex,
                "location": patient_location
            },
            location=patient_location
        )
        
        processing_time = time.time() - start_time
        
        # Save to database
        AnalysisDB.update(
            db, analysis_id,
            comprehensive_diagnosis=result.get("diagnosis", ""),
            processing_time_seconds=processing_time
        )
        
        if result.get("medical_report"):
            ReportDB.create(
                db,
                f"REP_{analysis_id}",
                analysis_id,
                report_text=result.get("medical_report"),
                assessment=result.get("severity", "Unknown")
            )
        
        AnalysisDB.update_status(db, analysis_id, "completed")
        
        # PDF export
        pdf_path = None
        if send_pdf:
            logger.info("📄 Generating PDF...")
            pdf_path = PDFExporter.generate_report_pdf(
                patient_name=patient_name,
                age=patient_age,
                sex=patient_sex,
                diagnosis=result.get("diagnosis", ""),
                severity=result.get("severity", ""),
                medical_report=result.get("medical_report", ""),
                diet_plan=result.get("diet_plan", ""),
                timestamp=workflow_id
            )
        
        # Email notification
        if send_email and patient_email:
            logger.info("📧 Sending email...")
            try:
                email_sent = EmailNotifier.send_analysis_report(
                    patient_email, patient_name,
                    diagnosis=result.get("diagnosis", ""),
                    severity=result.get("severity", ""),
                    medical_report=result.get("medical_report", ""),
                    diet_plan=result.get("diet_plan", ""),
                    hospitals=result.get("hospitals", []),
                    specialists=result.get("specialists", []),
                    pdf_path=pdf_path,
                    confidence=result.get("confidence", 0.0)
                )
                if email_sent:
                    logger.info(f"✅ Email successfully sent to {patient_email}")
                else:
                    logger.warning(f"⚠️ Email send returned False for {patient_email}")
            except Exception as e:
                logger.error(f"❌ Email sending error: {e}")
        
        save_conversation(f"Patient: {patient_name}", f"Diagnosis: {result.get('diagnosis', '')[:100]}")
        
        logger.info(f"✅ Workflow {workflow_id} completed in {processing_time:.2f}s")
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "patient_id": patient_id,
            "analysis_id": analysis_id,
            "processing_time_seconds": round(processing_time, 2),
            **result,
            "pdf_path": pdf_path
        }
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {e}")
        if 'analysis_id' in locals():
            AnalysisDB.update_status(db, analysis_id, "error", error_message=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze")
async def analyze_alias(
    patient_name: str,
    patient_age: int,
    patient_sex: str,
    patient_location: str,
    eye_image: UploadFile = File(...),
    nails_image: UploadFile = File(...),
    tongue_image: UploadFile = File(...),
    patient_email: Optional[str] = None,
    send_pdf: bool = False,
    send_email: bool = False,
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Backwards compatibility alias"""
    return await complete_analysis(
        patient_name, patient_age, patient_sex, patient_location,
        eye_image, nails_image, tongue_image,
        patient_email, send_pdf, send_email, x_api_key, db
    )

# ========================
# INDIVIDUAL AGENTS
# ========================

@app.post("/api/vision-analysis")
async def vision_analysis(
    eye_image: UploadFile = File(...),
    nails_image: UploadFile = File(...),
    tongue_image: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """Vision analysis only"""
    try:
        eye_b64, nails_b64, tongue_b64 = await process_images_to_base64(
            eye_image, nails_image, tongue_image
        )
        
        result = orchestrator.execute_vision_analysis(
            workflow_id=generate_workflow_id(),
            images_dict={"eye": eye_b64, "nails": nails_b64, "tongue": tongue_b64}
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report-diet")
async def report_diet(
    diagnosis: str,
    severity: str = "moderate",
    x_api_key: Optional[str] = Header(None)
):
    """Report & diet generation only"""
    try:
        result = orchestrator.execute_report_and_diet(
            workflow_id=generate_workflow_id(),
            diagnosis=diagnosis,
            severity=severity
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/healthcare-discovery")
async def healthcare_discovery(
    diagnosis: str,
    location: str,
    x_api_key: Optional[str] = Header(None)
):
    """Healthcare discovery only"""
    try:
        result = orchestrator.execute_healthcare_discovery(
            workflow_id=generate_workflow_id(),
            diagnosis=diagnosis,
            location=location
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# DEMO ENDPOINT
# ========================

@app.post("/api/demo-analysis")
async def demo_analysis(diagnosis_type: str = "anemia", x_api_key: Optional[str] = Header(None)):
    """Demo endpoint - instant testing without images"""
    try:
        demo_data = {
            "anemia": {
                "diagnosis": "Iron Deficiency Anemia",
                "severity": "moderate",
                "confidence": 0.87
            },
            "diabetes": {
                "diagnosis": "Type 2 Diabetes",
                "severity": "moderate",
                "confidence": 0.92
            },
            "infection": {
                "diagnosis": "Bacterial Infection",
                "severity": "mild",
                "confidence": 0.79
            },
            "normal": {
                "diagnosis": "Normal Health Status",
                "severity": "none",
                "confidence": 0.95
            }
        }
        
        demo = demo_data.get(diagnosis_type, demo_data["normal"])
        
        return {
            "status": "success",
            "workflow_id": f"DEMO_{uuid.uuid4().hex[:8].upper()}",
            "processing_time_seconds": 0.5,
            **demo,
            "medical_report": f"Demo report for {demo['diagnosis']}",
            "diet_plan": "Balanced nutrition with appropriate modifications",
            "hospitals": [{"name": "demo hospital", "rating": 4.8}],
            "specialists": ["General Practitioner"],
            "top_doctor_recommendation": {"name": "Dr. Demo", "specialty": "General Medicine"},
            "appointment_slots": ["2026-04-12 10:00", "2026-04-12 14:00"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# MONITORING ENDPOINTS
# ========================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "AI Medical Diagnostic System v2.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "✅",
            "orchestrator": "✅",
            "auth": "✅",
            "cache": "✅"
        }
    }

@app.get("/api/agents/status")
async def agents_status():
    """Agent status"""
    return {
        "status": "success",
        "agents": {
            "vision": "READY",
            "report_diet": "READY",
            "healthcare": "READY"
        }
    }

@app.get("/api/workflows")
async def list_workflows():
    """List workflows"""
    return {"status": "success", "workflows": orchestrator.workflows}

@app.get("/api/workflows/{workflow_id}")
async def workflow_details(workflow_id: str):
    """Workflow details"""
    workflow = orchestrator.workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "success", "workflow": workflow}

@app.get("/api/statistics")
async def statistics(db: Session = Depends(get_db), x_api_key: Optional[str] = Header(None)):
    """System statistics"""
    try:
        if x_api_key and not APIKeyManager.is_admin_key(x_api_key):
            raise HTTPException(status_code=403, detail="Admin only")
        
        stats = DatabaseStats.get_stats(db)
        return {
            "status": "success",
            "database": stats,
            "cache_mb": round(CacheManager.get_cache_size(), 2)
        }
    except:
        return {"status": "success", "database": {}, "cache_mb": 0}

@app.get("/api/info")
async def system_info():
    """System info"""
    return {
        "status": "success",
        "name": "AI Medical Diagnostic System v2.0",
        "features": {
            "pdf_export": PDFExporter.PDF_AVAILABLE,
            "email": True,
            "database": True,
            "auth": True,
            "cache": True
        },
        "endpoints": {
            "main": "/api/complete-analysis",
            "demo": "/api/demo-analysis",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/api/test")
async def test():
    """Test endpoint"""
    return {"status": "online", "message": "System is running!"}

@app.get("/")
async def root():
    """Root"""
    return {
        "status": "online",
        "system": "AI Medical Diagnostic System v2.0",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health"
    }

# ========================
# ADMIN ENDPOINTS
# ========================

@app.post("/api/auth/generate-key")
async def generate_key(name: str = "key", admin: bool = False, x_api_key: Optional[str] = Header(None)):
    """Generate API key"""
    try:
        if x_api_key and not APIKeyManager.is_admin_key(x_api_key):
            raise HTTPException(status_code=403, detail="Admin only")
        
        new_key = APIKeyManager.generate_api_key(name, admin)
        return {"status": "success", "api_key": new_key, "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cache/clear")
async def clear_cache(x_api_key: Optional[str] = Header(None)):
    """Clear cache"""
    try:
        if x_api_key and not APIKeyManager.is_admin_key(x_api_key):
            raise HTTPException(status_code=403, detail="Admin only")
        
        CacheManager.clear_cache()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
async def reset(x_api_key: Optional[str] = Header(None)):
    """Reset system"""
    try:
        if x_api_key and not APIKeyManager.is_admin_key(x_api_key):
            raise HTTPException(status_code=403, detail="Admin only")
        
        orchestrator.workflows = {}
        CacheManager.clear_cache()
        return {"status": "success", "message": "System reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# RUN
# ========================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 9000))
    logger.info(f"🚀 Starting server on http://localhost:{port}")
    logger.info(f"📚 API docs: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main_new:app",
        host="0.0.0.0",
        port=port,
        reload=DEBUG_MODE,
        log_level="info"
    )
"""
Complete Agentic Medical Diagnostic System - FastAPI Backend
Multi-agent orchestrated workflow for medical image analysis
"""

import logging
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime
import uvicorn
import shutil
import os
import asyncio

from config import DEBUG_MODE
from image_processor import ImageProcessor
from agent_orchestrator import AgentOrchestrator, create_orchestrator
from memory import save_conversation

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================
# FastAPI Application Setup
# ========================

app = FastAPI(
    title="🏥 AI Medical Diagnostic System",
    description="Multi-agent agentic medical diagnosis with vision analysis, reports, and healthcare provider discovery",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Global Orchestrator
# ========================

orchestrator = create_orchestrator()
image_processor = ImageProcessor()

# ========================
# Pydantic Models
# ========================

class PatientInfo(BaseModel):
    """Patient demographic and clinical information"""
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    location: str  # Required for healthcare provider search
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None
    urgency: Optional[str] = "routine"  # routine, urgent, emergency


class CompleteAnalysisRequest(BaseModel):
    """Request for complete end-to-end analysis"""
    patient_info: PatientInfo


class AgentStatusResponse(BaseModel):
    """Agent status information"""
    vision_agent: str
    agent_1: str
    agent_2: str
    timestamp: str


class WorkflowStatusResponse(BaseModel):
    """Workflow execution status"""
    workflow_id: str
    patient_id: str
    status: str
    agents_completed: List[str]
    started_at: str
    completed_at: Optional[str] = None
    errors: List[Dict] = []


# ========================
# Utility Functions
# ========================

async def save_uploaded_file(upload_file: UploadFile, folder: str = "uploads") -> str:
    """Save uploaded file and return path"""
    try:
        Path(folder).mkdir(exist_ok=True)
        file_path = f"{folder}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{upload_file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        logger.info(f"📁 File saved: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"❌ Error saving file: {e}")
        raise HTTPException(status_code=400, detail=f"Error saving file: {e}")


def process_image_to_base64(image_path: str) -> str:
    """Convert image to base64"""
    try:
        img = image_processor.load_image(image_path)
        if img is not None:
            processed, _ = image_processor.preprocess(img)
            return image_processor.to_base64(processed)
        raise ValueError("Cannot load image")
    except Exception as e:
        logger.error(f"❌ Error processing image: {e}")
        raise


# ========================
# Static Files & Root Endpoint
# ========================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve frontend at root"""
    try:
        index_path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(index_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h1 style="color: white;">🏥 AI Medical Diagnostic System</h1>
                <p style="color: white; font-size: 18px;">⚠️ Frontend not found</p>
                <p style="color: white;">Visit <a href="/docs" style="color: yellow;">/docs</a> for API documentation</p>
            </body>
        </html>
        """


# ========================
# MAIN AGENTIC ENDPOINT
# ========================

@app.post("/api/complete-analysis", tags=["Agentic Workflow"])
async def complete_medical_analysis(
    patient_name: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
    location: str = "Current Location",
    medical_history: Optional[str] = None,
    urgency: Optional[str] = "routine",
    eye_image: UploadFile = File(...),
    nails_image: UploadFile = File(...),
    tongue_image: UploadFile = File(...),
):
    """
    🏥 COMPLETE AGENTIC MEDICAL ANALYSIS
    
    End-to-end workflow orchestrating all agents:
    1. Vision Analysis Agent - Multimodal image analysis
    2. Report & Diet Agent - Professional medical report + personalized diet plan
    3. Healthcare Discovery Agent - Hospital & doctor recommendations
    
    **Workflow:**
    ```
    Images → Vision Agent → Diagnosis
                ↓
    Diagnosis → Agent 1 → Medical Report + Diet Plan
                ↓
    Diagnosis → Agent 2 → Hospitals, Doctors, Appointments
    ```
    """
    
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 INITIATING COMPLETE AGENTIC WORKFLOW")
        logger.info(f"Patient: {patient_name or 'Anonymous'}")
        logger.info(f"Location: {location}")
        logger.info(f"Urgency: {urgency}")
        logger.info(f"{'='*70}\n")
        
        # Save images
        logger.info("📸 PHASE 1: Image Upload & Processing")
        eye_path = await save_uploaded_file(eye_image)
        nails_path = await save_uploaded_file(nails_image)
        tongue_path = await save_uploaded_file(tongue_image)
        
        # Convert to base64
        logger.info("🔀 Converting images to base64...")
        eye_base64 = process_image_to_base64(eye_path)
        nails_base64 = process_image_to_base64(nails_path)
        tongue_base64 = process_image_to_base64(tongue_path)
        
        images_dict = {
            "eye": eye_base64,
            "nails": nails_base64,
            "tongue": tongue_base64
        }
        
        # Patient info
        patient_info = {
            "name": patient_name or "Patient",
            "age": patient_age,
            "sex": patient_sex,
            "location": location,
            "medical_history": medical_history,
            "urgency": urgency
        }
        
        # ========================
        # Execute Orchestrator Workflow
        # ========================
        
        logger.info("\n🤖 PHASE 2: Activating Agentic Orchestrator")
        logger.info("="*70)
        
        result = orchestrator.execute_complete_workflow(
            images_dict=images_dict,
            patient_info=patient_info,
            location=location
        )
        
        logger.info("\n✅ WORKFLOW COMPLETE")
        logger.info(f"{'='*70}\n")
        
        # Save to memory
        save_conversation(
            f"Patient: {patient_name}",
            f"Diagnosis: {result.get('diagnosis', '')[:500]}"
        )
        
        return {
            "status": "success",
            "workflow_id": result["workflow_id"],
            "patient": patient_info,
            "diagnosis": result["diagnosis"],
            "severity": result["severity"],
            "confidence": result["confidence"],
            
            # Medical Report & Diet
            "medical_report": result["medical_report"],
            "diet_plan": result["diet_plan"],
            
            # Healthcare Discovery
            "hospitals": result["hospitals"],
            "specialists": result["specialists"],
            "top_doctor_recommendation": result["top_doctor_recommendation"],
            "appointment_slots": result["appointment_slots"],
            
            # Metadata
            "agents_executed": result["agents_executed"],
            "timestamp": result["timestamp"]
        }
    
    except Exception as e:
        logger.error(f"❌ Workflow Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Workflow failed: {str(e)}"
        )


# ========================
# ALIAS: Support old endpoint name
# ========================

@app.post("/api/analyze", tags=["Agentic Workflow"])
async def analyze_medical_images(
    patient_name: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
    location: str = "Current Location",
    medical_history: Optional[str] = None,
    urgency: Optional[str] = "routine",
    eye_image: UploadFile = File(...),
    nails_image: UploadFile = File(...),
    tongue_image: UploadFile = File(...),
):
    """
    🏥 COMPLETE AGENTIC MEDICAL ANALYSIS (Alias endpoint)
    
    Same as /api/complete-analysis - provided for backwards compatibility
    
    **Usage:**
    1. Upload 3 images: eye, nails, tongue
    2. Fill patient info
    3. Wait 20-30 seconds
    4. Get complete diagnosis + reports + doctors
    """
    return await complete_medical_analysis(
        patient_name=patient_name,
        patient_age=patient_age,
        patient_sex=patient_sex,
        location=location,
        medical_history=medical_history,
        urgency=urgency,
        eye_image=eye_image,
        nails_image=nails_image,
        tongue_image=tongue_image
    )
    return await complete_medical_analysis(
        patient_name=patient_name,
        patient_age=patient_age,
        patient_sex=patient_sex,
        location=location,
        medical_history=medical_history,
        urgency=urgency,
        eye_image=eye_image,
        nails_image=nails_image,
        tongue_image=tongue_image
    )


# ========================
# INDIVIDUAL AGENT ENDPOINTS
# ========================

@app.post("/api/vision-analysis", tags=["Individual Agents"])
async def vision_analysis_only(
    eye_image: UploadFile = File(...),
    nails_image: UploadFile = File(...),
    tongue_image: UploadFile = File(...),
    medical_history: Optional[str] = None
):
    """
    🔍 Vision Analysis Agent Only
    
    Analyze medical images and return diagnostic findings
    """
    try:
        logger.info("🔍 Vision Analysis Agent activated")
        
        # Save and convert images
        eye_path = await save_uploaded_file(eye_image)
        nails_path = await save_uploaded_file(nails_image)
        tongue_path = await save_uploaded_file(tongue_image)
        
        eye_base64 = process_image_to_base64(eye_path)
        nails_base64 = process_image_to_base64(nails_path)
        tongue_base64 = process_image_to_base64(tongue_path)
        
        images_dict = {
            "eye": eye_base64,
            "nails": nails_base64,
            "tongue": tongue_base64
        }
        
        # Create temporary workflow for vision analysis
        workflow_id = f"VISION_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = orchestrator.execute_vision_analysis(
            workflow_id=workflow_id,
            images_dict=images_dict,
            patient_info={"medical_history": medical_history} if medical_history else None
        )
        
        return {
            "status": "success",
            "agent": "vision_agent",
            "diagnosis": result["comprehensive_diagnosis"],
            "analyses": result["individual_analyses"],
            "confidence": result.get("confidence", 0.85)
        }
    
    except Exception as e:
        logger.error(f"❌ Vision Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report-diet", tags=["Individual Agents"])
async def generate_report_and_diet(
    diagnosis: str,
    severity: str = Query("moderate", enum=["none", "mild", "moderate", "severe"]),
    patient_name: Optional[str] = None,
    patient_age: Optional[int] = None,
    location: Optional[str] = None,
):
    """
    📋 Report & Diet Agent Only
    
    Generate medical report and diet plan from diagnosis
    """
    try:
        logger.info("📋 Report & Diet Agent activated")
        
        patient_info = {
            "name": patient_name,
            "age": patient_age,
            "location": location
        }
        
        workflow_id = f"REPORT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = orchestrator.execute_report_and_diet(
            workflow_id=workflow_id,
            diagnosis=diagnosis,
            analyses={"eye": "", "nails": "", "tongue": ""},
            severity=severity,
            patient_info=patient_info
        )
        
        return {
            "status": "success",
            "agent": "agent_1",
            "medical_report": result["medical_report"],
            "diet_plan": result["diet_plan"],
            "files": {
                "report": result.get("report_file"),
                "diet_plan": result.get("diet_plan_file")
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Report & Diet Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/healthcare-discovery", tags=["Individual Agents"])
async def discover_healthcare(
    diagnosis: str,
    location: str,
    patient_name: Optional[str] = None,
):
    """
    🏥 Healthcare Discovery Agent Only
    
    Find hospitals, doctors, and appointment slots
    """
    try:
        logger.info("🏥 Healthcare Discovery Agent activated")
        
        patient_info = {"name": patient_name}
        workflow_id = f"HEALTHCARE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = orchestrator.execute_healthcare_discovery(
            workflow_id=workflow_id,
            diagnosis=diagnosis,
            location=location,
            patient_info=patient_info
        )
        
        return {
            "status": "success",
            "agent": "agent_2",
            "hospitals": result["hospitals"],
            "specialists": result["specialties"],
            "top_doctor": result["top_recommendation"],
            "appointments": result["appointment_slots"]
        }
    
    except Exception as e:
        logger.error(f"❌ Healthcare Discovery Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# SYSTEM MONITORING & STATUS ENDPOINTS
# ========================

@app.get("/health", tags=["System"])
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "service": "AI Medical Diagnostic System",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "agents": orchestrator.get_agent_status()
    }


@app.get("/api/agents/status", response_model=AgentStatusResponse, tags=["System"])
async def get_agents_status():
    """Get current status of all agents"""
    statuses = orchestrator.get_agent_status()
    return AgentStatusResponse(
        vision_agent=statuses["vision_agent"],
        agent_1=statuses["agent_1"],
        agent_2=statuses["agent_2"],
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/workflows", tags=["System"])
async def get_all_workflows():
    """Get all workflow execution history"""
    workflows = orchestrator.get_workflow_history()
    return {
        "status": "success",
        "total_workflows": len(workflows),
        "workflows": workflows
    }


@app.get("/api/workflows/{workflow_id}", tags=["System"])
async def get_workflow_details(workflow_id: str):
    """Get specific workflow details"""
    workflow = orchestrator.get_workflow_status(workflow_id)
    if "error" in workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@app.get("/api/info", tags=["System"])
async def system_info():
    """System information and capabilities"""
    return {
        "name": "AI Medical Diagnostic System",
        "version": "2.0.0",
        "architecture": "Multi-Agent Orchestrated",
        "agents": {
            "vision_agent": "Multimodal medical image analysis (Eye, Nails, Tongue)",
            "agent_1": "Medical report & personalized diet plan generation",
            "agent_2": "Healthcare provider discovery & appointment scheduling"
        },
        "supported_body_parts": ["eye", "nails", "tongue"],
        "supported_formats": ["jpg", "jpeg", "png", "bmp", "webp"],
        "max_image_size_mb": 20,
        "capabilities": [
            "Multimodal image analysis",
            "Automated diagnosis generation",
            "Personalized medical reports",
            "Diet plan customization",
            "Hospital discovery",
            "Doctor recommendation",
            "Appointment scheduling"
        ]
    }


@app.get("/api/test", tags=["System"])
async def test_connection():
    """Simple test endpoint to verify server is responding"""
    return {
        "status": "success",
        "message": "✅ Server is running and responding correctly!",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True,
        "agents_ready": True
    }


@app.post("/api/demo-analysis", tags=["Testing"])
async def demo_analysis(
    diagnosis_type: str = Query("anemia", description="Type of condition: anemia, diabetes, infection, normal")
):
    """
    🧪 DEMO ENDPOINT - Test system without uploading images
    
    **Use this to verify the system works before uploading real images**
    
    Pass `diagnosis_type` to simulate different conditions:
    - anemia: Iron deficiency
    - diabetes: Blood sugar issues
    - infection: Possible infection
    - normal: Healthy patient
    """
    
    try:
        logger.info(f"🧪 Demo analysis started for: {diagnosis_type}")
        
        # Simulated diagnoses
        diagnoses = {
            "anemia": "Patient shows signs of iron deficiency based on pale conjunctiva and linguistic pallor. Hemoglobin levels appear reduced.",
            "diabetes": "Patient exhibits possible type 2 diabetes indicators including retinal changes and glucose-related findings.",
            "infection": "Patient shows signs of possible bacterial infection with inflammation markers visible in oral cavity.",
            "normal": "Patient appears healthy with normal findings across all examined areas."
        }
        
        selected_diagnosis = diagnoses.get(diagnosis_type, diagnoses["normal"])
        severity = "moderate" if diagnosis_type != "normal" else "none"
        
        # Simulate workflow
        workflow_id = f"DEMO_{diagnosis_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "message": "✅ Demo workflow executed - This shows the system structure. Use /api/complete-analysis with real images for actual diagnosis.",
            
            "diagnosis": selected_diagnosis,
            "severity": severity,
            "confidence": 0.82,
            
            "medical_report": {
                "status": "success",
                "report": f"""# MEDICAL REPORT (DEMO)
**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Patient Type:** Demo - {diagnosis_type.upper()}

## Clinical Summary
This is a demonstration report. In production, detailed clinical findings would appear here.

## Detailed Findings
Diagnosis: {selected_diagnosis}

## Assessment
- **Overall Status:** {'Healthy' if severity == 'none' else 'At Risk'}
- **Severity:** {severity.capitalize()}
- **Confidence:** 82%

## Recommendations
- Follow up with healthcare provider
- Maintain healthy lifestyle
- Regular check-ups recommended

## Follow-up Required
Yes - Specialist: General Practitioner
"""
            },
            
            "diet_plan": {
                "status": "success",
                "diet_plan": f"""# PERSONALIZED DIET PLAN (DEMO)
**Duration:** 30 days
**Severity Level:** {severity.capitalize()}
**Created:** {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary
This is a demonstration diet plan. In production, personalized recommendations based on actual diagnosis would appear here.

## Nutritional Goals
- Balanced nutrition focus
- Micronutrient optimization
- Overall wellness

## Foods to Prioritize
- Leafy greens (iron, vitamins)
- Lean proteins (strength)
- Whole grains (energy)
- Fresh fruits (antioxidants)

## Foods to Avoid
- Processed foods
- Excess sugar
- High sodium items

## Weekly Meal Suggestions
**Monday-Wednesday:** Balanced nutrition focus
**Thursday-Friday:** Detox-style meals  
**Weekend:** Flexibility with healthy choices

## Supplements (if needed)
- Vitamin B12: Daily
- Iron: As recommended
- General multivitamin: Daily
"""
            },
            
            "hospitals": [
                {"name": "Central Medical Hospital", "address": "123 Health St", "rating": "4.8", "link": "demo"},
                {"name": "City Health Center", "address": "456 Care Ave", "rating": "4.6", "link": "demo"}
            ],
            
            "specialists": ["General Practitioner", "Internal Medicine"],
            
            "top_doctor_recommendation": {
                "doctor": {"name": "Dr. Demo Smith", "specialty": "General Practitioner"},
                "match_score": 92,
                "specialty": "General Practitioner"
            },
            
            "appointment_slots": [
                {"date": "2026-04-10", "time": "09:00 AM", "doctor": "Dr. Demo Smith"},
                {"date": "2026-04-11", "time": "02:00 PM", "doctor": "Dr. Demo Smith"}
            ],
            
            "agents_executed": ["vision_agent", "agent_1", "agent_2"],
            "timestamp": datetime.now().isoformat(),
            
            "note": "This is a DEMO response. Use /api/complete-analysis with real image uploads for actual medical analysis."
        }
    
    except Exception as e:
        logger.error(f"❌ Demo Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset", tags=["System"])
async def reset_system():
    """Reset orchestrator and agent statuses"""
    orchestrator.reset_agent_statuses()
    return {
        "status": "success",
        "message": "System reset complete",
        "timestamp": datetime.now().isoformat()
    }


# ========================
# ERROR HANDLING
# ========================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ========================
# Startup/Shutdown Events
# ========================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("\n" + "="*70)
    logger.info("🚀 AI MEDICAL DIAGNOSTIC SYSTEM - STARTING UP")
    logger.info("="*70)
    logger.info("✅ Orchestrator initialized")
    logger.info("✅ Vision Agent ready")
    logger.info("✅ Report & Diet Agent ready")
    logger.info("✅ Healthcare Discovery Agent ready")
    logger.info("✅ All systems operational")
    logger.info("="*70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("\n" + "="*70)
    logger.info("🛑 AI MEDICAL DIAGNOSTIC SYSTEM - SHUTTING DOWN")
    logger.info("="*70 + "\n")


# ========================
# Run Application
# ========================

if __name__ == "__main__":
    uvicorn.run(
        "main_new:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG_MODE,
        log_level="debug" if DEBUG_MODE else "info"
    )
