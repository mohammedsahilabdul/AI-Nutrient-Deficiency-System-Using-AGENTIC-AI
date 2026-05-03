"""
Agent Orchestrator - Coordinates all agents for complete medical diagnosis workflow
This is the master controller that manages multi-agent collaboration
"""

import logging
import uuid
from typing import Dict, Optional, Any, List
from datetime import datetime
from enum import Enum
import asyncio

from vision_agent import DiagnosisAgent
from agent_report_diet import Agent1_ReportAndDiet
from agent_hospital_doctor import Agent2_HospitalDoctor
from memory import save_conversation

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


class AgentOrchestrator:
    """
    Master conductor for all medical diagnosis agents
    Orchestrates Vision Agent → Agent 1 → Agent 2 workflow
    """
    
    def __init__(self):
        self.orchestrator_id = f"ORK_{uuid.uuid4().hex[:8]}"
        self.vision_agent = DiagnosisAgent()
        self.agent_1 = Agent1_ReportAndDiet()
        self.agent_2 = Agent2_HospitalDoctor()
        
        # Status tracking
        self.workflow_status: Dict[str, Dict[str, Any]] = {}
        self.agent_statuses: Dict[str, AgentStatus] = {
            "vision_agent": AgentStatus.IDLE,
            "agent_1": AgentStatus.IDLE,
            "agent_2": AgentStatus.IDLE
        }
        
        logger.info(f"✅ Agent Orchestrator initialized: {self.orchestrator_id}")
    
    def start_workflow(self, patient_id: str) -> str:
        """Start a new workflow and return workflow ID"""
        
        workflow_id = f"WF_{patient_id}_{uuid.uuid4().hex[:8]}"
        self.workflow_status[workflow_id] = {
            "id": workflow_id,
            "patient_id": patient_id,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "status": "running",
            "agents_completed": [],
            "errors": [],
            "results": {}
        }
        
        logger.info(f"🚀 Workflow started: {workflow_id}")
        return workflow_id
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow status"""
        return self.workflow_status.get(
            workflow_id,
            {"error": "Workflow not found", "status": "error"}
        )
    
    # ========================
    # STAGE 1: Vision Analysis
    # ========================
    
    def execute_vision_analysis(
        self,
        workflow_id: str,
        images_dict: Dict[str, str],  # {"eye": base64, "nails": base64, "tongue": base64}
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute Vision Agent for image analysis
        
        Args:
            workflow_id: Unique workflow identifier
            images_dict: Base64 encoded images by body part
            patient_info: Optional patient context
        
        Returns:
            Vision analysis results
        """
        
        logger.info(f"📍 Stage 1: Starting Vision Analysis (Workflow: {workflow_id})")
        self.agent_statuses["vision_agent"] = AgentStatus.PROCESSING
        
        try:
            # Run comprehensive diagnosis
            vision_result = self.vision_agent.generate_comprehensive_diagnosis(images_dict)
            
            self.agent_statuses["vision_agent"] = AgentStatus.COMPLETED
            self.workflow_status[workflow_id]["agents_completed"].append("vision_agent")
            self.workflow_status[workflow_id]["results"]["vision"] = vision_result
            
            logger.info(f"✅ Vision Analysis Complete")
            
            return {
                "status": "success",
                "agent": "vision_agent",
                "comprehensive_diagnosis": vision_result.get("comprehensive_diagnosis"),
                "individual_analyses": vision_result.get("individual_analyses"),
                "confidence": vision_result.get("confidence", 0.85)
            }
        
        except Exception as e:
            logger.error(f"❌ Vision Agent Error: {e}")
            self.agent_statuses["vision_agent"] = AgentStatus.ERROR
            self.workflow_status[workflow_id]["errors"].append({
                "agent": "vision_agent",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    # ========================
    # STAGE 2: Report & Diet Generation
    # ========================
    
    def execute_report_and_diet(
        self,
        workflow_id: str,
        diagnosis: str,
        analyses: Dict[str, str],
        severity: str = "moderate",
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute Agent 1 for report and diet plan generation
        
        Args:
            workflow_id: Unique workflow identifier
            diagnosis: Comprehensive diagnosis from vision analysis
            analyses: Individual body part analyses
            severity: Condition severity assessment
            patient_info: Patient demographic and medical data
        
        Returns:
            Report and diet plan
        """
        
        logger.info(f"📍 Stage 2: Starting Report & Diet Generation (Workflow: {workflow_id})")
        self.agent_statuses["agent_1"] = AgentStatus.PROCESSING
        
        try:
            agent1_result = self.agent_1.execute(
                diagnosis=diagnosis,
                analyses=analyses,
                condition_severity=severity,
                patient_info=patient_info
            )
            
            self.agent_statuses["agent_1"] = AgentStatus.COMPLETED
            self.workflow_status[workflow_id]["agents_completed"].append("agent_1")
            self.workflow_status[workflow_id]["results"]["agent_1"] = agent1_result
            
            logger.info(f"✅ Report & Diet Generation Complete")
            
            return agent1_result
        
        except Exception as e:
            logger.error(f"❌ Agent 1 Error: {e}")
            self.agent_statuses["agent_1"] = AgentStatus.ERROR
            self.workflow_status[workflow_id]["errors"].append({
                "agent": "agent_1",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    # ========================
    # STAGE 3: Hospital & Doctor Finding
    # ========================
    
    def execute_healthcare_discovery(
        self,
        workflow_id: str,
        diagnosis: str,
        location: str,
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute Agent 2 for healthcare provider discovery
        
        Args:
            workflow_id: Unique workflow identifier
            diagnosis: Comprehensive diagnosis
            location: Patient location for provider search
            patient_info: Patient information for relevance
        
        Returns:
            Hospitals, doctors, and appointment options
        """
        
        logger.info(f"📍 Stage 3: Starting Healthcare Discovery (Workflow: {workflow_id})")
        self.agent_statuses["agent_2"] = AgentStatus.PROCESSING
        
        try:
            agent2_result = self.agent_2.execute(
                diagnosis=diagnosis,
                location=location,
                patient_info=patient_info
            )
            
            self.agent_statuses["agent_2"] = AgentStatus.COMPLETED
            self.workflow_status[workflow_id]["agents_completed"].append("agent_2")
            self.workflow_status[workflow_id]["results"]["agent_2"] = agent2_result
            
            logger.info(f"✅ Healthcare Discovery Complete")
            
            return agent2_result
        
        except Exception as e:
            logger.error(f"❌ Agent 2 Error: {e}")
            self.agent_statuses["agent_2"] = AgentStatus.ERROR
            self.workflow_status[workflow_id]["errors"].append({
                "agent": "agent_2",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    # ========================
    # COMPLETE WORKFLOW EXECUTION
    # ========================
    
    def execute_complete_workflow(
        self,
        images_dict: Dict[str, str],
        patient_info: Dict[str, Any],
        location: str
    ) -> Dict[str, Any]:
        """
        Execute complete multi-agent workflow end-to-end
        
        Flow:
            1. Vision Agent analyzes images
            2. Agent 1 generates reports and diet plans
            3. Agent 2 finds hospitals and doctors
        
        Args:
            images_dict: Base64 encoded medical images
            patient_info: Complete patient information
            location: Location for provider search
        
        Returns:
            Complete analysis with all agent outputs
        """
        
        # Start workflow
        patient_id = patient_info.get("name", "unknown").replace(" ", "_")
        workflow_id = self.start_workflow(patient_id)
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🏥 COMPLETE MEDICAL DIAGNOSIS WORKFLOW INITIATED")
            logger.info(f"Workflow ID: {workflow_id}")
            logger.info(f"Patient: {patient_info.get('name', 'Unknown')}")
            logger.info(f"{'='*60}\n")
            
            # ========================
            # STAGE 1: Vision Analysis
            # ========================
            logger.info("📸 STAGE 1: MULTIMODAL IMAGE ANALYSIS")
            logger.info("-" * 60)
            
            vision_result = self.execute_vision_analysis(
                workflow_id,
                images_dict,
                patient_info
            )
            
            diagnosis = vision_result["comprehensive_diagnosis"]
            individual_analyses = vision_result["individual_analyses"]
            severity = self._assess_severity(diagnosis)
            
            logger.info(f"Diagnosis Summary: {diagnosis[:200]}...")
            logger.info(f"Severity Level: {severity}")
            
            # ========================
            # STAGE 2: Report & Diet
            # ========================
            logger.info("\n📋 STAGE 2: PERSONAL HEALTH REPORT & DIET PLAN GENERATION")
            logger.info("-" * 60)
            
            agent1_result = self.execute_report_and_diet(
                workflow_id,
                diagnosis,
                {
                    "eye": individual_analyses.get("eye", {}).get("analysis", ""),
                    "nails": individual_analyses.get("nails", {}).get("analysis", ""),
                    "tongue": individual_analyses.get("tongue", {}).get("analysis", "")
                },
                severity,
                patient_info
            )
            
            logger.info(f"Report Generated: {agent1_result['report_file'] or 'In-memory'}")
            if agent1_result.get('diet_plan_file'):
                logger.info(f"Diet Plan Generated: {agent1_result['diet_plan_file']}")
            
            # ========================
            # STAGE 3: Healthcare Discovery
            # ========================
            logger.info("\n🏥 STAGE 3: HEALTHCARE PROVIDER DISCOVERY")
            logger.info("-" * 60)
            
            agent2_result = self.execute_healthcare_discovery(
                workflow_id,
                diagnosis,
                location,
                patient_info
            )
            
            hospitals = agent2_result.get("hospitals", [])
            top_doctor = agent2_result.get("top_recommendation", {}).get("doctor")
            
            logger.info(f"Hospitals Found: {len(hospitals)}")
            if top_doctor:
                logger.info(f"Recommended Doctor: {top_doctor.get('name', 'N/A')}")
            
            # ========================
            # CONSOLIDATE RESULTS
            # ========================
            
            self.workflow_status[workflow_id]["status"] = "completed"
            self.workflow_status[workflow_id]["completed_at"] = datetime.now().isoformat()
            
            # Extract text from nested dicts (for frontend display and email)
            medical_report_text = ""
            if agent1_result.get("medical_report"):
                if isinstance(agent1_result["medical_report"], dict):
                    medical_report_text = agent1_result["medical_report"].get("report", "")
                else:
                    medical_report_text = str(agent1_result["medical_report"])
            
            diet_plan_text = ""
            if agent1_result.get("diet_plan"):
                if isinstance(agent1_result["diet_plan"], dict):
                    diet_plan_text = agent1_result["diet_plan"].get("diet_plan", "")
                else:
                    diet_plan_text = str(agent1_result["diet_plan"])
            
            consolidated_result = {
                "status": "success",
                "workflow_id": workflow_id,
                "patient_info": patient_info,
                "timestamp": datetime.now().isoformat(),
                
                # Vision Analysis Results
                "diagnosis": diagnosis,
                "vision_analyses": individual_analyses,
                "confidence": vision_result.get("confidence", 0.85),
                "severity": severity,
                
                # Agent 1 Results - TEXT FORMAT for display
                "medical_report": medical_report_text,
                "diet_plan": diet_plan_text,
                "report_file": agent1_result.get("report_file"),
                "diet_plan_file": agent1_result.get("diet_plan_file"),
                
                # Agent 2 Results
                "hospitals": hospitals,
                "specialists": agent2_result.get("specialties", []),
                "top_doctor_recommendation": agent2_result.get("top_recommendation", {}),
                "appointment_slots": agent2_result.get("appointment_slots", []),
                
                # Workflow Metadata
                "agents_executed": self.workflow_status[workflow_id]["agents_completed"],
                "workflow_status": self.workflow_status[workflow_id]
            }
            
            # Save to memory
            save_conversation(
                f"Complete Workflow: {patient_info.get('name')}",
                f"Diagnosis: {diagnosis[:500]}"
            )
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info(f"Workflow ID: {workflow_id}")
            logger.info(f"Total Duration: {self._calculate_duration(workflow_id)}")
            logger.info(f"{'='*60}\n")
            
            return consolidated_result
        
        except Exception as e:
            logger.error(f"\n❌ WORKFLOW FAILED: {e}")
            self.workflow_status[workflow_id]["status"] = "error"
            self.workflow_status[workflow_id]["completed_at"] = datetime.now().isoformat()
            
            raise
    
    # ========================
    # UTILITY METHODS
    # ========================
    
    def _assess_severity(self, diagnosis: str) -> str:
        """Assess condition severity from diagnosis"""
        
        diagnosis_lower = diagnosis.lower()
        
        if "severe" in diagnosis_lower or "critical" in diagnosis_lower or "urgent" in diagnosis_lower:
            return "severe"
        elif "mild" in diagnosis_lower or "minor" in diagnosis_lower or "normal" in diagnosis_lower or "healthy" in diagnosis_lower:
            return "none"
        else:
            return "moderate"
    
    def _calculate_duration(self, workflow_id: str) -> str:
        """Calculate workflow duration"""
        
        workflow = self.workflow_status.get(workflow_id, {})
        started = workflow.get("started_at")
        completed = workflow.get("completed_at")
        
        if started and completed:
            start_dt = datetime.fromisoformat(started)
            end_dt = datetime.fromisoformat(completed)
            duration = (end_dt - start_dt).total_seconds()
            return f"{duration:.1f} seconds"
        
        return "N/A"
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get current status of all agents"""
        return {agent: status.value for agent, status in self.agent_statuses.items()}
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get all workflow execution history"""
        return list(self.workflow_status.values())
    
    def reset_agent_statuses(self):
        """Reset all agent statuses after workflow completion"""
        for agent in self.agent_statuses:
            self.agent_statuses[agent] = AgentStatus.IDLE
        logger.info("✅ Agent statuses reset")


# Convenience function
def create_orchestrator() -> AgentOrchestrator:
    """Create and return a new orchestrator instance"""
    return AgentOrchestrator()
