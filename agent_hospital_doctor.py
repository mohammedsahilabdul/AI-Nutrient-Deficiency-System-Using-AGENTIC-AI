"""
Agent 2: Hospital & Doctor Finder using Web Search
Finds nearest hospitals, suitable specialists, and schedules appointments
"""

import json
import logging
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime, timedelta
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from google_search_results import GoogleSearchResults
except ImportError:
    GoogleSearchResults = None

from config import SERPER_API_KEY, LLM_MODEL, ANTHROPIC_API_KEY, GROQ_API_KEY, USE_GROQ


class WebSearchEngine:
    """Handle web searches for hospitals and doctors"""
    
    def __init__(self, api_key: str = SERPER_API_KEY):
        self.api_key = api_key
        self.base_url = "https://google.search-api.serper.dev"
    
    def search_hospitals(self, location: str, specialty: Optional[str] = None) -> List[Dict]:
        """Search for hospitals near location"""
        
        query = f"hospitals near {location}"
        if specialty:
            query += f" {specialty}"
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers={"X-API-KEY": self.api_key},
                json={"q": query},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get("organic", [])
                
                hospitals = []
                for result in results[:5]:
                    hospitals.append({
                        "name": result.get("title"),
                        "address": result.get("snippet"),
                        "link": result.get("link"),
                        "rating": result.get("rating", "N/A")
                    })
                
                return hospitals
            else:
                logger.error(f"Search error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error searching hospitals: {e}")
            return []
    
    def search_doctors(self, specialty: str, location: str) -> List[Dict]:
        """Search for doctors by specialty and location"""
        
        query = f"{specialty} doctors near {location}"
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers={"X-API-KEY": self.api_key},
                json={"q": query},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get("organic", [])
                
                doctors = []
                for result in results[:5]:
                    doctors.append({
                        "name": result.get("title"),
                        "details": result.get("snippet"),
                        "link": result.get("link"),
                        "rating": result.get("rating", "N/A")
                    })
                
                return doctors
            else:
                logger.error(f"Search error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error searching doctors: {e}")
            return []
    
    def search_appointments(self, doctor_name: str, location: str) -> List[Dict]:
        """Search for available appointments"""
        
        query = f"{doctor_name} appointments available {location}"
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers={"X-API-KEY": self.api_key},
                json={"q": query},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get("organic", [])
                
                appointments = []
                for result in results[:3]:
                    appointments.append({
                        "service": result.get("title"),
                        "info": result.get("snippet"),
                        "link": result.get("link")
                    })
                
                return appointments
            else:
                logger.error(f"Search error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error searching appointments: {e}")
            return []


class DoctorRecommender:
    """Recommend best doctors based on diagnosis"""
    
    SPECIALTY_MAP = {
        "anemia": ["Hematologist", "General Practitioner"],
        "jaundice": ["Hepatologist", "Gastroenterologist", "Internal Medicine"],
        "diabetes": ["Endocrinologist", "Internal Medicine"],
        "hypertension": ["Cardiologist", "Internal Medicine"],
        "infection": ["Infectious Disease", "General Practitioner"],
        "allergies": ["Allergist", "Dermatologist"],
        "inflammation": ["Rheumatologist", "Internal Medicine"],
        "deficiency": ["Nutritionist", "Internal Medicine"],
        "default": ["General Practitioner"]
    }
    
    def __init__(self):
        if USE_GROQ:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
                self.model = "mixtral-8x7b-32768"
                logger.info("✓ Doctor Recommender using Groq (Free)")
            except Exception as e:
                logger.error(f"Failed to init Groq: {e}")
                self.client = None
        else:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                self.model = LLM_MODEL
                logger.info("Doctor Recommender using Anthropic Claude")
            except Exception as e:
                logger.error(f"Failed to init Anthropic: {e}")
                self.client = None
        
        self.search = WebSearchEngine()
    
    def get_specialties(self, diagnosis: str) -> List[str]:
        """Get relevant specialties for diagnosis"""
        
        diagnosis_lower = diagnosis.lower()
        
        for condition, specialties in self.SPECIALTY_MAP.items():
            if condition in diagnosis_lower:
                return specialties
        
        return self.SPECIALTY_MAP["default"]
    
    def rank_doctors(self, doctors: List[Dict], diagnosis: str) -> List[Dict]:
        """Rank doctors using LLM"""
        
        if not doctors:
            return []
        
        ranking_prompt = f"""Rank these doctors for treating {diagnosis}.
Consider their specialty, experience lhoices[0].message.contenippets), and patient reviews.

Doctors:
{json.dumps([{'name': d.get('name'), 'details': d.get('details')[:200]} for d in doctors[:5]], indent=2)}

Provide ranking with explanations as JSON:
[{{"rank": 1, "doctor": "name", "match_score": 95, "reason": "..."}}]
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": ranking_prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON
            try:
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    ranked = json.loads(json_match.group(0))
                    
                    # Merge with original doctor data
                    result = []
                    for rank_entry in ranked:
                        doctor_match = next(
                            (d for d in doctors if d.get('name', '').lower() in rank_entry.get('doctor', '').lower()),
                            None
                        )
                        if doctor_match:
                            doctor_match['match_score'] = rank_entry.get('match_score', 0)
                            doctor_match['reason'] = rank_entry.get('reason', '')
                            result.append(doctor_match)
                    
                    return result
            except:
                pass
            
            return doctors
        
        except Exception as e:
            logger.error(f"Error ranking doctors: {e}")
            return doctors


class AppointmentScheduler:
    """Schedule appointments with doctors"""
    
    def __init__(self):
        self.appointments = []
    
    def suggest_appointment_times(self, doctor_name: str, days_ahead: int = 7) -> List[Dict]:
        """Suggest available appointment times"""
        
        times = []
        slot_times = ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM"]
        
        for day_offset in range(1, days_ahead):
            date = datetime.now() + timedelta(days=day_offset)
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            for time_slot in slot_times:
                times.append({
                    "doctor": doctor_name,
                    "date": date.strftime("%Y-%m-%d"),
                    "time": time_slot,
                    "datetime": f"{date.strftime('%Y-%m-%d')} {time_slot}",
                    "available": True
                })
        
        return times[:5]  # Return first 5 slots
    
    def create_appointment(
        self,
        doctor_name: str,
        hospital: str,
        date: str,
        time: str,
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create appointment record"""
        
        appointment = {
            "id": f"APT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "doctor": doctor_name,
            "hospital": hospital,
            "date": date,
            "time": time,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "patient_info": patient_info or {},
            "reminder_sent": False
        }
        
        self.appointments.append(appointment)
        logger.info(f"Appointment created: {appointment['id']}")
        
        return appointment
    
    def send_reminder(self, appointment_id: str) -> bool:
        """Send reminder for appointment"""
        
        try:
            appointment = next(
                (apt for apt in self.appointments if apt['id'] == appointment_id),
                None
            )
            
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return False
            
            reminder_msg = f"""
APPOINTMENT REMINDER
Doctor: {appointment['doctor']}
Hospital: {appointment['hospital']}
Date: {appointment['date']} at {appointment['time']}

Please arrive 15 minutes early.
"""
            
            logger.info(f"Reminder for {appointment_id}: {reminder_msg}")
            appointment['reminder_sent'] = True
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            return False


class Agent2_HospitalDoctor:
    """
    Coordinated Agent 2 for finding hospitals and doctors
    """
    
    def __init__(self):
        self.recommender = DoctorRecommender()
        self.scheduler = AppointmentScheduler()
        self.search = WebSearchEngine()
    
    def execute(
        self,
        diagnosis: str,
        location: str,
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute complete Agent 2 workflow
        
        Returns:
            Hospitals, doctors, and appointment options
        """
        
        logger.info("🤖 Agent 2 executing: Hospital & Doctor Finder")
        
        # Get relevant specialties
        logger.info("🔍 Finding relevant specialists...")
        specialties = self.recommender.get_specialties(diagnosis)
        
        # Search for hospitals
        logger.info("🏥 Searching hospitals...")
        hospitals = self.search.search_hospitals(location, specialties[0] if specialties else None)
        
        # Search for doctors
        doctors_by_specialty = {}
        for specialty in specialties[:2]:  # Top 2 specialties
            logger.info(f"👨‍⚕️ Searching {specialty}...")
            doctors = self.search.search_doctors(specialty, location)
            
            # Rank doctors
            ranked = self.recommender.rank_doctors(doctors, diagnosis)
            doctors_by_specialty[specialty] = ranked
        
        # Get top doctor
        top_doctor = None
        top_specialty = None
        max_score = 0
        
        for specialty, doctors in doctors_by_specialty.items():
            for doc in doctors:
                score = doc.get('match_score', 0)
                if score > max_score:
                    max_score = score
                    top_doctor = doc
                    top_specialty = specialty
        
        # Suggest appointment times
        appointment_slots = None
        if top_doctor:
            appointment_slots = self.scheduler.suggest_appointment_times(
                top_doctor.get('name', 'Doctor')
            )
        
        result = {
            "status": "success",
            "agent": "Agent_2_HospitalDoctor",
            "diagnosis": diagnosis,
            "location": location,
            "hospitals": hospitals[:3],  # Top 3 hospitals
            "specialties": specialties,
            "doctors_by_specialty": doctors_by_specialty,
            "top_recommendation": {
                "doctor": top_doctor,
                "specialty": top_specialty,
                "match_score": max_score
            },
            "appointment_slots": appointment_slots,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ Agent 2 execution complete")
        
        return result
    
    def create_appointment_from_search(
        self,
        doctor_name: str,
        hospital_name: str,
        appointment_date: str,
        appointment_time: str,
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create appointment from search results"""
        
        return self.scheduler.create_appointment(
            doctor_name,
            hospital_name,
            appointment_date,
            appointment_time,
            patient_info
        )


# Convenience function
def find_healthcare_providers(
    diagnosis: str,
    location: str,
    patient_info: Optional[Dict] = None
) -> Dict[str, Any]:
    """Find hospitals and doctors for given diagnosis"""
    agent = Agent2_HospitalDoctor()
    return agent.execute(diagnosis, location, patient_info)
