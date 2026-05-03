"""
Main FastAPI Application
Coordinates all agents and provides REST API endpoints
"""

import logging
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime
import uvicorn
import shutil
import os

from config import DEBUG_MODE
from image_processor import ImageProcessor, MultiModalImageAnalyzer
from vision_agent import get_diagnosis_agent
from agent_report_diet import Agent1_ReportAndDiet
from agent_hospital_doctor import Agent2_HospitalDoctor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Medical Diagnostic System",
    description="Medical diagnosis using multimodal image analysis and agentic AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Serve Static Files (index.html)
# ========================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve index.html at root to enable camera access"""
    try:
        index_path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(index_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body style="text-align: center; padding: 50px; font-family: Arial;">
                <h1>🏥 AI Medical Diagnostic System</h1>
                <p>⚠️ index.html not found in project root</p>
                <p>Make sure index.html is in: {project_root}/index.html</p>
            </body>
        </html>
        """

# ========================
# Pydantic Models
# ========================

class PatientInfo(BaseModel):
    """Patient demographic and health information"""
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    location: Optional[str] = ""
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = None
    medication: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None


class AnalysisRequest(BaseModel):
    """Request body for medical analysis"""
    patient_info: PatientInfo
    location: str  # For hospital search
    urgency: Optional[str] = "routine"  # routine, urgent, emergency


class AnalysisResponse(BaseModel):
    """Response from analysis"""
    status: str
    diagnosis: Optional[str] = None
    analyses: Optional[Dict] = None
    report: Optional[str] = None
    diet_plan: Optional[str] = None
    hospitals: Optional[List[Dict]] = None
    doctors: Optional[List[Dict]] = None
    appointments: Optional[List[Dict]] = None
    error: Optional[str] = None


# ========================
# Initialize Agents
# ========================

image_processor = ImageProcessor()
multimodal_analyzer = MultiModalImageAnalyzer()
diagnosis_agent = get_diagnosis_agent()
agent_1 = Agent1_ReportAndDiet()
agent_2 = Agent2_HospitalDoctor()


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
        
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=400, detail=f"Error saving file: {e}")


def process_images_to_base64(file_paths: Dict[str, str]) -> Dict[str, str]:
    """Convert image files to base64 for LLM"""
    base64_images = {}
    
    for part, path in file_paths.items():
        try:
            img = image_processor.load_image(path)
            if img is not None:
                processed, _ = image_processor.preprocess(img)
                b64 = image_processor.to_base64(processed)
                base64_images[part] = b64
        except Exception as e:
            logger.error(f"Error processing {part}: {e}")
    
    return base64_images


# ========================
# API Endpoints
# ========================

@app.get("/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "AI Medical Diagnostic System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload_images": "/api/analyze",
            "health": "/health",
            "reports": "/reports/{report_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "agent_1": "Report & Diet Plan Generator",
            "agent_2": "Hospital & Doctor Finder"
        }
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_medical_images(
    eye_image: UploadFile = File(...),
    nails_image: UploadFile = File(...),
    tongue_image: UploadFile = File(...),
    patient_name: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
    location: str = "Current Location",
    medical_history: Optional[str] = None
):
    """
    Analyze medical images (eye, nails, tongue) and generate diagnosis with recommendations
    """
    
    try:
        logger.info(f"🔄 Starting analysis for patient: {patient_name}")
        
        # Save uploaded files
        eye_path = await save_uploaded_file(eye_image)
        nails_path = await save_uploaded_file(nails_image)
        tongue_path = await save_uploaded_file(tongue_image)
        
        logger.info("📸 Images saved")
        
        # Analyze images with multimodal processor
        patient_info = PatientInfo(
            name=patient_name,
            age=patient_age,
            sex=patient_sex,
            location=location,
            medical_history=medical_history
        )
        
        # Process images to base64
        file_paths = {
            "eye": eye_path,
            "nails": nails_path,
            "tongue": tongue_path
        }
        
        base64_images = process_images_to_base64(file_paths)
        
        logger.info("🔍 Performing vision analysis...")
        
        # Get comprehensive diagnosis
        diagnosis_result = diagnosis_agent.generate_comprehensive_diagnosis(base64_images)
        
        comprehensive_diagnosis = diagnosis_result.get("comprehensive_diagnosis", "")
        individual_analyses = diagnosis_result.get("individual_analyses", {})
        
        logger.info("✅ Diagnosis complete")
        
        # Determine severity
        severity = "moderate"
        if "normal" in comprehensive_diagnosis.lower() or "healthy" in comprehensive_diagnosis.lower():
            severity = "none"
        elif "urgent" in comprehensive_diagnosis.lower() or "severe" in comprehensive_diagnosis.lower():
            severity = "severe"
        
        # ========================
        # AGENT 1: Report & Diet Plan
        # ========================
        logger.info("🤖 Activating Agent 1: Report & Diet Plan Generator")
        
        agent1_result = agent_1.execute(
            diagnosis=comprehensive_diagnosis,
            analyses={
                "eye": individual_analyses.get("eye", {}).get("analysis", ""),
                "nails": individual_analyses.get("nails", {}).get("analysis", ""),
                "tongue": individual_analyses.get("tongue", {}).get("analysis", "")
            },
            condition_severity=severity,
            patient_info=patient_info.dict()
        )
        
        report = agent1_result.get("medical_report", {}).get("report", "")
        diet_plan = agent1_result.get("diet_plan", {}).get("diet_plan", "") if agent1_result.get("diet_plan") else None
        
        # ========================
        # AGENT 2: Hospital & Doctor Finder
        # ========================
        logger.info("🤖 Activating Agent 2: Hospital & Doctor Finder")
        
        agent2_result = agent_2.execute(
            diagnosis=comprehensive_diagnosis,
            location=location,
            patient_info=patient_info.dict()
        )
        
        hospitals = agent2_result.get("hospitals", [])
        top_recommendation = agent2_result.get("top_recommendation", {})
        appointment_slots = agent2_result.get("appointment_slots", [])
        
        logger.info("✅ All agents executed successfully")
        
        return AnalysisResponse(
            status="success",
            diagnosis=comprehensive_diagnosis,
            analyses=individual_analyses,
            report=report,
            diet_plan=diet_plan,
            hospitals=hospitals,
            doctors=[top_recommendation] if top_recommendation.get("doctor") else [],
            appointments=appointment_slots
        )
    
    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
        return AnalysisResponse(
            status="error",
            error=str(e)
        )


@app.post("/api/single-image")
async def analyze_single_image(
    image: UploadFile = File(...),
    body_part: str = "tongue",
    medical_history: Optional[str] = None
):
    """
    Analyze single image (eye, nails, or tongue)
    """
    
    try:
        # Save file
        image_path = await save_uploaded_file(image)
        
        # Process image
        img = image_processor.load_image(image_path)
        processed, _ = image_processor.preprocess(img)
        b64 = image_processor.to_base64(processed)
        
        # Analyze with vision agent
        diagnosis_agent_instance = get_diagnosis_agent()
        analysis = diagnosis_agent_instance.vision_agent.analyze_medical_image(b64, body_part)
        
        return {
            "status": "success",
            "body_part": body_part,
            "analysis": analysis.get("analysis"),
            "image_path": image_path
        }
    
    except Exception as e:
        logger.error(f"Error analyzing single image: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/reports")
async def list_reports():
    """List all generated reports"""
    try:
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        files = list(reports_dir.glob("*.md"))
        
        return {
            "status": "success",
            "count": len(files),
            "reports": [
                {
                    "filename": f.name,
                    "created": f.stat().st_mtime,
                    "size": f.stat().st_size
                }
                for f in sorted(files, reverse=True)[:20]
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{report_name}")
async def get_report(report_name: str):
    """Get specific report file"""
    try:
        report_path = Path("reports") / report_name
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            report_path,
            media_type="text/markdown",
            filename=report_name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/book-appointment")
async def book_appointment(
    doctor_name: str,
    hospital_name: str,
    appointment_date: str,
    appointment_time: str,
    patient_name: Optional[str] = None,
    patient_email: Optional[str] = None
):
    """Book appointment with selected doctor"""
    try:
        appointment = agent_2.scheduler.create_appointment(
            doctor_name=doctor_name,
            hospital_name=hospital_name,
            date=appointment_date,
            time=appointment_time,
            patient_info={
                "name": patient_name,
                "email": patient_email
            }
        )
        
        return {
            "status": "success",
            "appointment": appointment,
            "confirmation_id": appointment.get("id")
        }
    
    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/stats")
async def get_statistics():
    """Get system statistics"""
    return {
        "status": "success",
        "uptime": datetime.now().isoformat(),
        "appointments_scheduled": len(agent_2.scheduler.appointments),
        "agents_active": ["Agent_1_ReportAndDiet", "Agent_2_HospitalDoctor"],
        "models_loaded": [
            "claude-3-5-sonnet-20241022 (Vision & LLM)"
        ]
    }


# ========================
# Error Handlers
# ========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "detail": exc.detail}
    )


# ========================
# Startup & Shutdown
# ========================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 Starting AI Medical Diagnostic System")
    logger.info("✅ All agents loaded and ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down AI Medical Diagnostic System")


# ========================
# Main
# ========================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info" if DEBUG_MODE else "error"
    )
