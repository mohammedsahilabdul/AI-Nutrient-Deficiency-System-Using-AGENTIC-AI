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
