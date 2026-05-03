"""
Streamlit Application for AI Medical Diagnostic System
Handles image uploads, diagnosis, appointment booking, and email notifications
With PDF report generation and doctor dataset integration
"""

import streamlit as st
import os
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from io import BytesIO

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Import custom modules
from config import (
    ANTHROPIC_API_KEY, GROQ_API_KEY, USE_GROQ, DEBUG_MODE,
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
)
from image_processor import ImageProcessor, MultiModalImageAnalyzer
from vision_agent import get_diagnosis_agent
from agent_report_diet import Agent1_ReportAndDiet
from agent_hospital_doctor import Agent2_HospitalDoctor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# Symptom to Specialty Mapping
# ========================
SYMPTOM_SPECIALTY_MAP = {
    "heart": ["Cardiologist"],
    "cardiac": ["Cardiologist"],
    "hypertension": ["Cardiologist"],
    "chest pain": ["Cardiologist"],
    "blood pressure": ["Cardiologist"],
    "brain": ["Neurologist"],
    "neurological": ["Neurologist"],
    "seizure": ["Neurologist"],
    "migraine": ["Neurologist"],
    "skin": ["Dermatologist"],
    "dermatological": ["Dermatologist"],
    "rash": ["Dermatologist"],
    "acne": ["Dermatologist"],
    "eczema": ["Dermatologist"],
    "bone": ["Orthopedic"],
    "joint": ["Orthopedic"],
    "fracture": ["Orthopedic"],
    "osteoporosis": ["Orthopedic"],
    "arthritis": ["Orthopedic"],
    "women": ["Gynecologist"],
    "pregnancy": ["Gynecologist"],
    "gynecological": ["Gynecologist"],
    "menstrual": ["Gynecologist"],
    "child": ["Pediatrician"],
    "pediatric": ["Pediatrician"],
    "infant": ["Pediatrician"],
    "baby": ["Pediatrician"],
    "ear": ["ENT Specialist"],
    "nose": ["ENT Specialist"],
    "throat": ["ENT Specialist"],
    "ent": ["ENT Specialist"],
    "general": ["General Physician"],
    "fever": ["General Physician"],
    "cold": ["General Physician"],
    "mental": ["Psychiatrist"],
    "depression": ["Psychiatrist"],
    "anxiety": ["Psychiatrist"],
    "psychiatric": ["Psychiatrist"],
}

# ========================
# Page Configuration
# ========================
st.set_page_config(
    page_title="🏥 AI Medical Diagnostic System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# Load Doctor Dataset
# ========================
@st.cache_data
def load_doctor_dataset():
    """Load doctor dataset from CSV"""
    try:
        df = pd.read_csv("doc_dataset.csv")
        # Keep only the first 3 columns (drop empty columns)
        df = df.iloc[:, :3]
        # Ensure correct column names
        df.columns = ["Doctor Names", "Specialty", "Cities"]
        return df
    except Exception as e:
        logger.error(f"Error loading doctor dataset: {e}")
        return pd.DataFrame()

def get_suitable_doctors(diagnosis: str, location: str = None):
    """Get doctors suitable for the diagnosis based on symptoms"""
    df = load_doctor_dataset()
    
    if df.empty:
        return []
    
    # Find matching specialties based on diagnosis keywords
    suitable_specialties = set()
    diagnosis_lower = diagnosis.lower()
    
    for symptom, specialties in SYMPTOM_SPECIALTY_MAP.items():
        if symptom in diagnosis_lower:
            suitable_specialties.update(specialties)
    
    # If no specific specialty found, include general physicians
    if not suitable_specialties:
        suitable_specialties.add("General Physician")
    
    # Filter doctors by specialty
    suitable_doctors = df[df["Specialty"].isin(suitable_specialties)].copy()
    
    # If no exact matches found, add general physicians
    if suitable_doctors.empty:
        general_docs = df[df["Specialty"] == "General Physician"]
        if not general_docs.empty:
            suitable_doctors = general_docs.copy()
        else:
            # Return all doctors if no general physicians found
            suitable_doctors = df.copy()
    else:
        # Also include general physicians along with specialists
        general_docs = df[df["Specialty"] == "General Physician"]
        if not general_docs.empty:
            suitable_doctors = pd.concat([suitable_doctors, general_docs], ignore_index=True)
    
    # Rename columns for display
    suitable_doctors.columns = ["Doctor Name", "Specialty", "City"]
    
    # Remove duplicates
    suitable_doctors = suitable_doctors.drop_duplicates(subset=['Doctor Name'])
    
    return suitable_doctors.to_dict('records')

# ========================
# PDF Report Generation
# ========================
class PDFReportGenerator:
    """Generate PDF reports for medical diagnosis and diet plan"""
    
    @staticmethod
    def generate_medical_report_pdf(patient_info: dict, diagnosis: str, report: str) -> BytesIO:
        """Generate medical report PDF"""
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        story.append(Paragraph("🏥 MEDICAL DIAGNOSTIC REPORT", header_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Info
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        story.append(Paragraph(f"<b>Patient Name:</b> {patient_info.get('name', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Age:</b> {patient_info.get('age', 'N/A')} years", info_style))
        story.append(Paragraph(f"<b>Sex:</b> {patient_info.get('sex', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Location:</b> {patient_info.get('location', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}", info_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Diagnosis Section
        story.append(Paragraph("<b><font size=14>PRIMARY DIAGNOSIS</font></b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        diagnosis_para = Paragraph(diagnosis, ParagraphStyle('DiagnosisText', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY))
        story.append(diagnosis_para)
        story.append(Spacer(1, 0.3*inch))
        
        # Medical Report Section
        story.append(Paragraph("<b><font size=14>DETAILED REPORT</font></b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        report_para = Paragraph(report, ParagraphStyle('ReportText', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY))
        story.append(report_para)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        story.append(Paragraph("This report is generated by AI Medical Diagnostic System and should be reviewed by qualified medical professionals.", footer_style))
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
    
    @staticmethod
    def generate_diet_plan_pdf(patient_info: dict, diet_plan: str) -> BytesIO:
        """Generate diet plan PDF"""
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        story.append(Paragraph("🍽️ PERSONALIZED DIET PLAN", header_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Info
        info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=11, spaceAfter=6)
        story.append(Paragraph(f"<b>Patient Name:</b> {patient_info.get('name', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Age:</b> {patient_info.get('age', 'N/A')} years", info_style))
        story.append(Paragraph(f"<b>Plan Date:</b> {datetime.now().strftime('%B %d, %Y')}", info_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Diet Plan Section
        story.append(Paragraph("<b><font size=14>DIETARY RECOMMENDATIONS</font></b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        diet_para = Paragraph(diet_plan, ParagraphStyle('DietText', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY))
        story.append(diet_para)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        story.append(Paragraph("Follow this diet plan under medical supervision. Consult your doctor before making significant dietary changes.", footer_style))
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer

# ========================
# Page Configuration
# ========================
st.set_page_config(
    page_title="🏥 AI Medical Diagnostic System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# Custom CSS
# ========================
st.markdown("""
    <style>
        .main {
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        }
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .error-box {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .info-box {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# ========================
# Initialize Session State
# ========================
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "images_uploaded" not in st.session_state:
    st.session_state.images_uploaded = False
if "appointment_booked" not in st.session_state:
    st.session_state.appointment_booked = False


class EmailNotifier:
    """Send email notifications with reports and appointments"""
    
    @staticmethod
    def send_email(recipient_email: str, subject: str, body: str, html_body: str = None, attachments: list = None) -> bool:
        """Send email with optional attachments (file paths or BytesIO objects)"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            msg.attach(MIMEText(body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    try:
                        if isinstance(attachment, BytesIO):
                            # BytesIO object (PDF buffer)
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.getvalue())
                            encoders.encode_base64(part)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"medical_report_{timestamp}.pdf"
                            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                            msg.attach(part)
                        elif isinstance(attachment, str) and os.path.exists(attachment):
                            # File path
                            with open(attachment, 'rb') as attach_file:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attach_file.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment)}')
                                msg.attach(part)
                    except Exception as e:
                        logger.error(f"Error attaching file: {e}")
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✓ Email sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    @staticmethod
    def send_appointment_confirmation(patient_email: str, appointment_details: dict, doctor_info: dict, attachments: list = None) -> bool:
        """Send appointment confirmation email with attachments"""
        subject = "🏥 Appointment Confirmation - AI Medical Diagnostic System"
        
        body = f"""
Dear {appointment_details.get('patient_name', 'Patient')},

Your appointment has been successfully booked!

APPOINTMENT DETAILS:
- Doctor: Dr. {doctor_info.get('name', 'N/A')}
- Specialty: {doctor_info.get('specialty', 'N/A')}
- Hospital: {doctor_info.get('city', 'N/A')}
- Date: {appointment_details.get('date', 'N/A')}
- Time: {appointment_details.get('time', 'N/A')}
- Location: {appointment_details.get('location', 'N/A')}

Please arrive 15 minutes before your appointment.

Medical Report and Diet Plan are attached to this email.

Best regards,
AI Medical Diagnostic System
"""
        
        html_body = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: white; border-radius: 10px 10px 0 0;">
            <h2 style="margin: 0;">🏥 Appointment Confirmation</h2>
        </div>
        <div style="padding: 20px; background: #f9f9f9;">
            <p>Dear <strong>{appointment_details.get('patient_name', 'Patient')}</strong>,</p>
            <p>Your appointment has been successfully booked! Please find your medical reports attached.</p>
            
            <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Appointment Details:</h3>
            <table style="width: 100%; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px; font-weight: bold; width: 40%;">Doctor:</td>
                    <td style="padding: 8px;">Dr. {doctor_info.get('name', 'N/A')}</td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 8px; font-weight: bold;">Specialty:</td>
                    <td style="padding: 8px;">{doctor_info.get('specialty', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Location:</td>
                    <td style="padding: 8px;">{doctor_info.get('city', 'N/A')}</td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 8px; font-weight: bold;">Date:</td>
                    <td style="padding: 8px;">{appointment_details.get('date', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Time:</td>
                    <td style="padding: 8px;">{appointment_details.get('time', 'N/A')}</td>
                </tr>
            </table>
            
            <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 0;"><strong>⏰ Note:</strong> Please arrive 15 minutes before your appointment.</p>
            </div>
            
            <p><strong>Your Medical Reports:</strong></p>
            <ul>
                <li>✓ Comprehensive Medical Report</li>
                <li>✓ Personalized Diet Plan</li>
            </ul>
            
            <hr style="border: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">This is an automated confirmation. If you have any questions, please contact the clinic directly.</p>
        </div>
    </body>
</html>
"""
        
        return EmailNotifier.send_email(patient_email, subject, body, html_body, attachments)


# ========================
# Main App Layout
# ========================
st.markdown("""
    <div class="header">
        <h1>🏥 AI Medical Diagnostic System</h1>
        <p>Advanced Medical Analysis with Appointment Booking</p>
    </div>
""", unsafe_allow_html=True)

# ========================
# Sidebar Navigation
# ========================
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio("Select Page:", ["Upload & Analyze", "View Results", "Book Appointment"])

# ========================
# PAGE 1: Upload & Analyze
# ========================
if page == "Upload & Analyze":
    st.header("📸 Upload Medical Images")
    
    with st.form("patient_info_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_name = st.text_input("Patient Name *", placeholder="Enter full name")
            patient_age = st.number_input("Age *", min_value=1, max_value=150, value=30)
        
        with col2:
            patient_sex = st.selectbox("Sex *", ["Male", "Female", "Other"])
            patient_email = st.text_input("Email Address *", placeholder="your.email@example.com")
        
        with col3:
            patient_location = st.text_input("Location/City *", placeholder="Enter your city")
            medical_history = st.text_area("Medical History", placeholder="Any relevant medical conditions", height=80)
        
        st.divider()
        st.subheader("📷 Upload Images (Max 10MB each)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("👁️ Eye Image")
            eye_image = st.file_uploader("Upload eye image", type=["jpg", "jpeg", "png"], key="eye")
        
        with col2:
            st.info("💅 Nails Image")
            nails_image = st.file_uploader("Upload nails image", type=["jpg", "jpeg", "png"], key="nails")
        
        with col3:
            st.info("👅 Tongue Image")
            tongue_image = st.file_uploader("Upload tongue image", type=["jpg", "jpeg", "png"], key="tongue")
        
        submit_button = st.form_submit_button("🔍 Analyze Images", use_container_width=True)
    
    if submit_button:
        # Validation
        if not all([patient_name, patient_age, patient_sex, patient_email, patient_location]):
            st.error("⚠️ Please fill in all required fields (marked with *)")
        elif not all([eye_image, nails_image, tongue_image]):
            st.error("⚠️ Please upload all three images")
        elif not "@" in patient_email:
            st.error("⚠️ Please enter a valid email address")
        else:
            # Start analysis
            with st.spinner("🔄 Analyzing images... This may take a minute..."):
                try:
                    # Create uploads directory
                    Path("uploads").mkdir(exist_ok=True)
                    
                    # Save uploaded files
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    eye_path = f"uploads/eye_{timestamp}.jpg"
                    nails_path = f"uploads/nails_{timestamp}.jpg"
                    tongue_path = f"uploads/tongue_{timestamp}.jpg"
                    
                    with open(eye_path, "wb") as f:
                        f.write(eye_image.getbuffer())
                    with open(nails_path, "wb") as f:
                        f.write(nails_image.getbuffer())
                    with open(tongue_path, "wb") as f:
                        f.write(tongue_image.getbuffer())
                    
                    logger.info("✓ Images saved")
                    
                    # Initialize processors and agents
                    image_processor = ImageProcessor()
                    multimodal_analyzer = MultiModalImageAnalyzer()
                    diagnosis_agent = get_diagnosis_agent()
                    agent_1 = Agent1_ReportAndDiet()
                    agent_2 = Agent2_HospitalDoctor()
                    
                    # Process images to base64
                    def process_image_to_base64(path):
                        img = image_processor.load_image(path)
                        if img is not None:
                            processed, _ = image_processor.preprocess(img)
                            return image_processor.to_base64(processed)
                        return None
                    
                    base64_images = {
                        "eye": process_image_to_base64(eye_path),
                        "nails": process_image_to_base64(nails_path),
                        "tongue": process_image_to_base64(tongue_path)
                    }
                    
                    logger.info("✓ Images processed")
                    st.info("✓ Images processed successfully")
                    
                    # Get diagnosis
                    st.info("🔍 Performing medical analysis...")
                    diagnosis_result = diagnosis_agent.generate_comprehensive_diagnosis(base64_images)
                    
                    comprehensive_diagnosis = diagnosis_result.get("comprehensive_diagnosis", "")
                    individual_analyses = diagnosis_result.get("individual_analyses", {})
                    
                    logger.info("✓ Diagnosis complete")
                    st.success("✓ Diagnosis analysis complete")
                    
                    # Determine severity
                    severity = "moderate"
                    if "normal" in comprehensive_diagnosis.lower() or "healthy" in comprehensive_diagnosis.lower():
                        severity = "none"
                    elif "urgent" in comprehensive_diagnosis.lower() or "severe" in comprehensive_diagnosis.lower():
                        severity = "severe"
                    
                    # Generate report and diet plan (Agent 1)
                    st.info("🤖 Generating medical report and diet plan...")
                    agent1_result = agent_1.execute(
                        diagnosis=comprehensive_diagnosis,
                        analyses={
                            "eye": individual_analyses.get("eye", {}).get("analysis", ""),
                            "nails": individual_analyses.get("nails", {}).get("analysis", ""),
                            "tongue": individual_analyses.get("tongue", {}).get("analysis", "")
                        },
                        condition_severity=severity,
                        patient_info={
                            "name": patient_name,
                            "age": patient_age,
                            "sex": patient_sex,
                            "location": patient_location,
                            "medical_history": medical_history
                        }
                    )
                    
                    report = agent1_result.get("medical_report", {}).get("report", "")
                    diet_plan = agent1_result.get("diet_plan", {}).get("diet_plan", "") if agent1_result.get("diet_plan") else None
                    
                    st.success("✓ Report and diet plan generated")
                    
                    # Find hospitals and doctors (Agent 2)
                    st.info("🤖 Finding suitable doctors and hospitals...")
                    agent2_result = agent_2.execute(
                        diagnosis=comprehensive_diagnosis,
                        location=patient_location,
                        patient_info={
                            "name": patient_name,
                            "age": patient_age,
                            "sex": patient_sex,
                            "location": patient_location
                        }
                    )
                    
                    hospitals = agent2_result.get("hospitals", [])
                    top_recommendation = agent2_result.get("top_recommendation", {})
                    appointment_slots = agent2_result.get("appointment_slots", [])
                    
                    st.success("✓ Doctors and hospitals found")
                    
                    # Store results in session state
                    st.session_state.analysis_results = {
                        "patient_name": patient_name,
                        "patient_age": patient_age,
                        "patient_sex": patient_sex,
                        "patient_email": patient_email,
                        "patient_location": patient_location,
                        "medical_history": medical_history,
                        "diagnosis": comprehensive_diagnosis,
                        "individual_analyses": individual_analyses,
                        "report": report,
                        "diet_plan": diet_plan,
                        "hospitals": hospitals,
                        "top_recommendation": top_recommendation,
                        "appointment_slots": appointment_slots,
                        "severity": severity,
                        "timestamp": timestamp,
                        "image_paths": {
                            "eye": eye_path,
                            "nails": nails_path,
                            "tongue": tongue_path
                        }
                    }
                    st.session_state.images_uploaded = True
                    
                    st.markdown("""
                        <div class="success-box">
                            <strong>✅ Analysis Complete!</strong><br>
                            Your medical analysis has been completed successfully. 
                            Go to "View Results" tab to see the details.
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                
                except Exception as e:
                    logger.error(f"❌ Error during analysis: {e}")
                    st.markdown(f"""
                        <div class="error-box">
                            <strong>❌ Error during analysis:</strong><br>
                            {str(e)}
                        </div>
                    """, unsafe_allow_html=True)

# ========================
# PAGE 2: View Results
# ========================
elif page == "View Results":
    if not st.session_state.images_uploaded or not st.session_state.analysis_results:
        st.warning("⚠️ No analysis results available. Please complete the analysis first on the 'Upload & Analyze' page.")
    else:
        results = st.session_state.analysis_results
        
        st.header("📋 Analysis Results")
        
        # Patient Information
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Patient Name", results["patient_name"])
        with col2:
            st.metric("Age", results["patient_age"])
        with col3:
            st.metric("Sex", results["patient_sex"])
        with col4:
            st.metric("Location", results["patient_location"])
        
        st.divider()
        
        # Download Reports Section
        st.subheader("📥 Download Reports")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Download Medical Report (PDF)", use_container_width=True):
                # Generate medical report PDF
                patient_info = {
                    "name": results["patient_name"],
                    "age": results["patient_age"],
                    "sex": results["patient_sex"],
                    "location": results["patient_location"]
                }
                pdf_buffer = PDFReportGenerator.generate_medical_report_pdf(
                    patient_info,
                    results["diagnosis"],
                    results["report"]
                )
                st.download_button(
                    label="⬇️ Download Medical Report",
                    data=pdf_buffer,
                    file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        
        with col2:
            if results["diet_plan"]:
                if st.button("🍽️ Download Diet Plan (PDF)", use_container_width=True):
                    # Generate diet plan PDF
                    patient_info = {
                        "name": results["patient_name"],
                        "age": results["patient_age"],
                        "sex": results["patient_sex"],
                        "location": results["patient_location"]
                    }
                    pdf_buffer = PDFReportGenerator.generate_diet_plan_pdf(
                        patient_info,
                        results["diet_plan"]
                    )
                    st.download_button(
                        label="⬇️ Download Diet Plan",
                        data=pdf_buffer,
                        file_name=f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
        
        st.divider()
        
        # Diagnosis
        st.subheader("🔍 Comprehensive Diagnosis")
        st.write(results["diagnosis"])
        
        # Individual Analyses
        st.subheader("📊 Individual Analyses")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("👁️ Eye Analysis")
            eye_analysis = results["individual_analyses"].get("eye", {}).get("analysis", "No data")
            st.write(eye_analysis)
        
        with col2:
            st.info("💅 Nails Analysis")
            nails_analysis = results["individual_analyses"].get("nails", {}).get("analysis", "No data")
            st.write(nails_analysis)
        
        with col3:
            st.info("👅 Tongue Analysis")
            tongue_analysis = results["individual_analyses"].get("tongue", {}).get("analysis", "No data")
            st.write(tongue_analysis)
        
        st.divider()
        
        # Medical Report
        st.subheader("📄 Medical Report")
        st.write(results["report"])
        
        # Diet Plan
        if results["diet_plan"]:
            st.subheader("🍽️ Personalized Diet Plan")
            st.write(results["diet_plan"])
        
        st.divider()
        
        # Hospital & Doctor Recommendations
        st.subheader("🏥 Recommended Doctors & Hospitals")
        
        if results["top_recommendation"]:
            st.success("✅ Top Recommendation")
            rec = results["top_recommendation"]
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Doctor:** {rec.get('doctor', 'N/A')}")
                st.write(f"**Hospital:** {rec.get('hospital', 'N/A')}")
            with col2:
                st.write(f"**Specialty:** {rec.get('specialty', 'N/A')}")
                st.write(f"**Rating:** {rec.get('rating', 'N/A')}")
        
        if results["hospitals"]:
            st.info("Other Nearby Hospitals:")
            for i, hospital in enumerate(results["hospitals"][:5], 1):
                with st.expander(f"Hospital {i}: {hospital.get('name', 'N/A')}"):
                    st.write(f"**Address:** {hospital.get('address', 'N/A')}")
                    st.write(f"**Rating:** {hospital.get('rating', 'N/A')}")
                    st.write(f"**Info:** {hospital.get('info', 'N/A')}")

# ========================
# PAGE 3: Book Appointment
# ========================
elif page == "Book Appointment":
    if not st.session_state.images_uploaded or not st.session_state.analysis_results:
        st.warning("⚠️ No analysis results available. Please complete the analysis first on the 'Upload & Analyze' page.")
    else:
        results = st.session_state.analysis_results
        
        st.header("📅 Book Appointment with Doctor")
        
        # Get suitable doctors based on diagnosis
        suitable_doctors = get_suitable_doctors(results["diagnosis"], results["patient_location"])
        
        if not suitable_doctors:
            st.warning("⚠️ No doctors available for this condition. Please try again later.")
        else:
            with st.form("appointment_form"):
                st.info(f"✓ Booking appointment for: **{results['patient_name']}**")
                st.info(f"✓ Condition identified from images: Based on symptoms, showing suitable doctors")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Doctor selection from dataset
                    doctor_options = [f"Dr. {d['Doctor Name']} ({d['Specialty']}) - {d['City']}" for d in suitable_doctors]
                    selected_doctor_option = st.selectbox(
                        "Select Doctor *",
                        doctor_options,
                        help="Doctors are filtered based on your condition"
                    )
                    
                    # Extract selected doctor details
                    selected_index = doctor_options.index(selected_doctor_option) if selected_doctor_option in doctor_options else 0
                    selected_doctor = suitable_doctors[selected_index]
                    
                    st.success(f"✓ Selected: Dr. {selected_doctor['Doctor Name']}")
                    st.caption(f"Specialty: {selected_doctor['Specialty']}")
                    st.caption(f"Location: {selected_doctor['City']}")
                
                with col2:
                    # Date and time selection
                    appointment_date = st.date_input(
                        "Preferred Date *",
                        min_value=datetime.now().date(),
                        value=datetime.now().date() + timedelta(days=1)
                    )
                    appointment_time = st.selectbox(
                        "Preferred Time *",
                        ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
                    )
                
                # Additional notes
                appointment_notes = st.text_area(
                    "Additional Notes/Concerns (Optional)",
                    placeholder="Any specific concerns or questions for the doctor",
                    height=80
                )
                
                st.divider()
                st.subheader("📎 Reports to be sent")
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("📄 Medical Report", value=True, disabled=True)
                with col2:
                    st.checkbox("🍽️ Diet Plan", value=True, disabled=True)
                st.caption("✓ Both reports will be attached to your confirmation email")
                
                submit_appointment = st.form_submit_button("✅ Confirm & Book Appointment", use_container_width=True)
            
            if submit_appointment:
                with st.spinner("⏳ Processing appointment booking and sending confirmation email with reports..."):
                    try:
                        # Generate PDFs
                        patient_info = {
                            "name": results["patient_name"],
                            "age": results["patient_age"],
                            "sex": results["patient_sex"],
                            "location": results["patient_location"]
                        }
                        
                        # Generate medical report PDF
                        medical_report_pdf = PDFReportGenerator.generate_medical_report_pdf(
                            patient_info,
                            results["diagnosis"],
                            results["report"]
                        )
                        
                        # Generate diet plan PDF
                        diet_plan_pdf = None
                        if results["diet_plan"]:
                            diet_plan_pdf = PDFReportGenerator.generate_diet_plan_pdf(
                                patient_info,
                                results["diet_plan"]
                            )
                        
                        # Create appointment record
                        appointment_details = {
                            "patient_name": results["patient_name"],
                            "patient_email": results["patient_email"],
                            "date": appointment_date.strftime("%B %d, %Y"),
                            "time": appointment_time,
                            "location": results["patient_location"],
                            "diagnosis": results["diagnosis"][:300],
                            "notes": appointment_notes
                        }
                        
                        doctor_info = {
                            "name": selected_doctor.get("Doctor Name", "N/A"),
                            "specialty": selected_doctor.get("Specialty", "General Medicine"),
                            "city": selected_doctor.get("City", "N/A")
                        }
                        
                        # Prepare attachments
                        attachments = [medical_report_pdf]
                        if diet_plan_pdf:
                            attachments.append(diet_plan_pdf)
                        
                        # Send confirmation email with PDF attachments
                        email_sent = EmailNotifier.send_appointment_confirmation(
                            results["patient_email"],
                            appointment_details,
                            doctor_info,
                            attachments=attachments
                        )
                        
                        if email_sent:
                            st.session_state.appointment_booked = True
                            
                            st.markdown("""
                                <div class="success-box">
                                    <strong>✅ Appointment Booked Successfully!</strong><br>
                                    Confirmation email with medical reports has been sent to your email address.
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Display booking summary
                            st.subheader("📋 Booking Summary")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Doctor:** Dr. {doctor_info['name']}")
                                st.write(f"**Specialty:** {doctor_info['specialty']}")
                                st.write(f"**Date:** {appointment_details['date']}")
                                st.write(f"**Time:** {appointment_time}")
                            
                            with col2:
                                st.write(f"**Patient:** {results['patient_name']}")
                                st.write(f"**Email:** {results['patient_email']}")
                                st.write(f"**City:** {doctor_info['city']}")
                                st.write(f"**Status:** ✅ Confirmed")
                            
                            st.divider()
                            st.success("✅ Medical Report and Diet Plan attached to confirmation email!")
                            st.info("📧 Check your email for booking confirmation and downloaded reports.")
                        else:
                            st.error("❌ Failed to send confirmation email. Please check your email configuration and try again.")
                    
                    except Exception as e:
                        logger.error(f"Error booking appointment: {e}")
                        st.error(f"❌ Error booking appointment: {str(e)}")
                        st.error(f"Details: {str(e)}")

# ========================
# Footer
# ========================
st.divider()
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px; padding: 20px;">
        <p>🏥 AI Medical Diagnostic System | Version 3.0</p>
        <p>For medical emergencies, please contact your nearest hospital immediately.</p>
        <p>This system is for diagnostic assistance only and should not replace professional medical advice.</p>
    </div>
""", unsafe_allow_html=True)
