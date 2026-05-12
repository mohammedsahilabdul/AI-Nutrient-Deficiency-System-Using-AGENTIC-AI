"""
Streamlit conversion of dashboard.html
Generates a multi-step medical diagnostic dashboard with image uploads,
review, results, appointment booking, email notifications, and calendar invites.
"""

import os
import logging
import base64
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import streamlit as st
import pandas as pd
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    DEBUG_MODE,
)
from image_processor import ImageProcessor
from vision_agent import get_diagnosis_agent
from agent_report_diet import Agent1_ReportAndDiet
from agent_hospital_doctor import Agent2_HospitalDoctor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ========================
# Helper functions
# ========================

def init_state():
    defaults = {
        "current_page": "Home",
        "current_step": 1,
        "patient_name": "",
        "patient_age": 30,
        "patient_sex": "Male",
        "patient_email": "",
        "patient_location": "",
        "patient_phone": "",
        "medical_history": "",
        "eye_image": None,
        "nails_image": None,
        "tongue_image": None,
        "analysis_results": None,
        "appointment_details": None,
        "email_status": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_doctor_dataset():
    try:
        df = pd.read_csv("doc_dataset.csv")
        df = df.iloc[:, :3]
        df.columns = ["Doctor Name", "Specialty", "City"]
        return df
    except Exception as e:
        logger.error(f"Error loading doctor dataset: {e}")
        return pd.DataFrame()


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


def get_suitable_doctors(diagnosis: str, location: str = None):
    df = load_doctor_dataset()
    if df.empty:
        return []

    diagnoses = diagnosis.lower()
    specialties = set()
    for symptom, specialty_list in SYMPTOM_SPECIALTY_MAP.items():
        if symptom in diagnoses:
            specialties.update(specialty_list)

    if not specialties:
        specialties.add("General Physician")

    filtered = df[df["Specialty"].isin(specialties)].copy()
    if filtered.empty:
        filtered = df[df["Specialty"] == "General Physician"].copy()
        if filtered.empty:
            filtered = df.copy()
    else:
        general = df[df["Specialty"] == "General Physician"].copy()
        if not general.empty:
            filtered = pd.concat([filtered, general], ignore_index=True)

    filtered = filtered.drop_duplicates(subset=["Doctor Name"])
    return filtered.to_dict("records")


class PDFReportGenerator:
    @staticmethod
    def generate_medical_report_pdf(patient_info: dict, diagnosis: str, report: str) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        header_style = ParagraphStyle(
            "Header",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#2563eb"),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("🏥 AI Medical Diagnostic Report", header_style))
        story.append(Spacer(1, 0.2 * inch))

        info_style = ParagraphStyle("Info", parent=styles["Normal"], fontSize=11, spaceAfter=6)
        story.append(Paragraph(f"<b>Patient Name:</b> {patient_info.get('name', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Age:</b> {patient_info.get('age', 'N/A')} years", info_style))
        story.append(Paragraph(f"<b>Sex:</b> {patient_info.get('sex', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Location:</b> {patient_info.get('location', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", info_style))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("<b>PRIMARY DIAGNOSIS</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(diagnosis or "No diagnosis available.", ParagraphStyle("NormalText", parent=styles["Normal"], fontSize=11, alignment=TA_JUSTIFY)))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("<b>DETAILED MEDICAL REPORT</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(report or "No report generated.", ParagraphStyle("NormalText", parent=styles["Normal"], fontSize=11, alignment=TA_JUSTIFY)))
        story.append(Spacer(1, 0.3 * inch))

        footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
        story.append(Paragraph("This report is generated for diagnostic assistance only.", footer_style))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_diet_plan_pdf(patient_info: dict, diet_plan: str) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        header_style = ParagraphStyle(
            "Header",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#764ba2"),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("🍽️ Personalized Diet Plan", header_style))
        story.append(Spacer(1, 0.2 * inch))

        info_style = ParagraphStyle("Info", parent=styles["Normal"], fontSize=11, spaceAfter=6)
        story.append(Paragraph(f"<b>Patient Name:</b> {patient_info.get('name', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Age:</b> {patient_info.get('age', 'N/A')} years", info_style))
        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", info_style))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("<b>PERSONALIZED DIET RECOMMENDATIONS</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(diet_plan or "No diet plan generated.", ParagraphStyle("NormalText", parent=styles["Normal"], fontSize=11, alignment=TA_JUSTIFY)))
        story.append(Spacer(1, 0.3 * inch))

        footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
        story.append(Paragraph("Consult a medical professional before making major dietary changes.", footer_style))

        doc.build(story)
        buffer.seek(0)
        return buffer


class EmailNotifier:
    @staticmethod
    def send_email(recipient_email: str, subject: str, body: str, attachments: list = None) -> bool:
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            logger.error("SMTP sender credentials are not configured.")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.getvalue())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={attachment.name}")
                    msg.attach(part)

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent to {recipient_email}")
            return True
        except Exception as exc:
            logger.error(f"Error sending email: {exc}")
            return False


def create_ics_content(appointment: dict) -> str:
    start_dt = datetime.combine(appointment["date"], appointment["time"])
    end_dt = start_dt + timedelta(hours=1)
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dtstart = start_dt.strftime("%Y%m%dT%H%M%SZ")
    dtend = end_dt.strftime("%Y%m%dT%H%M%SZ")
    uid = f"{datetime.utcnow().timestamp():.0f}@ai-medical-system"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AI Medical System//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"UID:{uid}",
        f"SUMMARY:Appointment with Dr. {appointment['doctor_name']}",
        f"LOCATION:{appointment['hospital']}",
        f"DESCRIPTION:Specialty: {appointment['specialty']}\\nNotes: {appointment.get('notes', 'None')}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines)


def save_uploaded_image(uploaded_file, prefix: str) -> str:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = Path(uploaded_file.name).suffix or ".jpg"
    output_path = uploads_dir / f"{prefix}_{timestamp}{extension}"
    with open(output_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(output_path)


def process_images(eye_path: str, nails_path: str, tongue_path: str) -> dict:
    image_processor = ImageProcessor()
    diagnosis_agent = get_diagnosis_agent()
    image_paths = {
        "eye": eye_path,
        "nails": nails_path,
        "tongue": tongue_path,
    }
    base64_images = {}
    for part, path in image_paths.items():
        img = image_processor.load_image(path)
        if img is not None:
            processed, _ = image_processor.preprocess(img)
            base64_images[part] = image_processor.to_base64(processed)
        else:
            base64_images[part] = ""

    diagnosis_result = diagnosis_agent.generate_comprehensive_diagnosis(base64_images)
    return diagnosis_result


def generate_result_summary():
    return {
        "Patient Name": st.session_state.patient_name,
        "Age": st.session_state.patient_age,
        "Sex": st.session_state.patient_sex,
        "Location": st.session_state.patient_location,
        "Email": st.session_state.patient_email,
        "Phone": st.session_state.patient_phone or "Not provided",
        "Medical History": st.session_state.medical_history or "No medical history provided",
    }


def validate_patient_info():
    missing = []
    if not st.session_state.patient_name.strip():
        missing.append("Patient Name")
    if not st.session_state.patient_age or st.session_state.patient_age < 1:
        missing.append("Age")
    if not st.session_state.patient_sex.strip():
        missing.append("Sex")
    if not st.session_state.patient_location.strip():
        missing.append("Location")
    if not st.session_state.patient_email.strip() or "@" not in st.session_state.patient_email:
        missing.append("Valid Email")
    return missing


def validate_uploads():
    missing = []
    if st.session_state.eye_image is None:
        missing.append("Eye image")
    if st.session_state.nails_image is None:
        missing.append("Nails image")
    if st.session_state.tongue_image is None:
        missing.append("Tongue image")
    return missing


# ========================
# UI helpers
# ========================

def render_progress_bar():
    step = st.session_state.current_step
    cols = st.columns(3)
    titles = ["Patient Info", "Upload Images", "Review & Analyze"]
    for index, (col, title) in enumerate(zip(cols, titles), start=1):
        label = f"{index}. {title}"
        if step == index:
            col.markdown(f"**✅ {label}**")
        elif step < index:
            col.markdown(f"🔵 {label}")
        else:
            col.markdown(f"✅ {label}")


def page_header():
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 14px; color: white; margin-bottom: 24px;'>
            <h1 style='margin: 0;'>🏥 AI Medical Diagnostic Dashboard</h1>
            <p style='margin: 8px 0 0;'>Multi-step diagnosis, upload, review, appointment booking, and email delivery.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_card():
    summary = generate_result_summary()
    st.markdown("### 📋 Review Summary")
    for label, value in summary.items():
        st.write(f"**{label}:** {value}")


# ========================
# Application layout
# ========================

st.set_page_config(page_title="AI Medical Dashboard", page_icon="🏥", layout="wide")
init_state()

st.markdown(
    """
    <style>
        .stButton>button { width: 100%; }
        .stDownloadButton>button { width: 100%; }
        .success-card { background: #ecfdf5; border: 1px solid #34d399; padding: 16px; border-radius: 12px; }
        .warning-card { background: #fef3c7; border: 1px solid #fbbf24; padding: 16px; border-radius: 12px; }
        .info-card { background: #cffafe; border: 1px solid #0ea5e9; padding: 16px; border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio("Navigation", ["Home", "Upload & Review", "View Results", "Book Appointment"])

if page != st.session_state.current_page:
    st.session_state.current_page = page

page_header()

if page == "Home":
    st.markdown("## Welcome")
    st.write("Start a new patient diagnosis flow, upload images, review results, and book appointments with email notifications.")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("What you can do")
        st.write("- Enter patient details and medical history")
        st.write("- Upload eye, nails, and tongue images")
        st.write("- Review information before AI analysis")
        st.write("- Download medical report and diet plan")
        st.write("- Book appointments and send email confirmations")
    with col2:
        if st.button("🚀 Start New Diagnosis"):
            st.session_state.current_page = "Upload & Review"
            st.experimental_rerun()

elif page == "Upload & Review":
    st.subheader("🧾 Patient Information & Image Upload")
    render_progress_bar()

    if st.session_state.current_step == 1:
        with st.form("patient_info_form"):
            st.markdown("### Patient Information")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Full Name *", key="patient_name")
                st.number_input("Age *", min_value=1, max_value=120, key="patient_age")
                st.selectbox("Sex *", ["Male", "Female", "Other"], key="patient_sex")
            with col2:
                st.text_input("Location/City *", key="patient_location")
                st.text_input("Email Address *", key="patient_email")
                st.text_input("Phone", key="patient_phone")
            st.text_area("Medical History", key="medical_history", height=120)
            submit = st.form_submit_button("Next: Upload Images →")
            if submit:
                missing = validate_patient_info()
                if missing:
                    st.warning("Please complete the required patient details: " + ", ".join(missing))
                else:
                    st.session_state.current_step = 2
                    st.experimental_rerun()

    elif st.session_state.current_step == 2:
        with st.form("image_upload_form"):
            st.markdown("### Upload Images")
            st.write("Upload clear images of each body part for accurate analysis.")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.file_uploader("Eye Image *", type=["jpg", "jpeg", "png"], key="eye_image")
                if st.session_state.eye_image:
                    st.write(f"Uploaded: {st.session_state.eye_image.name}")
            with col2:
                st.file_uploader("Nails Image *", type=["jpg", "jpeg", "png"], key="nails_image")
                if st.session_state.nails_image:
                    st.write(f"Uploaded: {st.session_state.nails_image.name}")
            with col3:
                st.file_uploader("Tongue Image *", type=["jpg", "jpeg", "png"], key="tongue_image")
                if st.session_state.tongue_image:
                    st.write(f"Uploaded: {st.session_state.tongue_image.name}")

            st.info("Maximum file size: 10MB. Use clear, well-lit photos for the best results.")
            cols = st.columns([1, 1])
            with cols[0]:
                if st.form_submit_button("← Previous"):
                    st.session_state.current_step = 1
                    st.experimental_rerun()
            with cols[1]:
                if st.form_submit_button("Next: Review & Analyze →"):
                    missing = validate_uploads()
                    if missing:
                        st.warning("Please upload the following images: " + ", ".join(missing))
                    else:
                        st.session_state.current_step = 3
                        st.experimental_rerun()

    elif st.session_state.current_step == 3:
        render_summary_card()
        st.warning("This AI analysis is for diagnostic assistance only and does not replace professional medical advice.")
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("← Previous"):
                st.session_state.current_step = 2
                st.experimental_rerun()
        with cols[1]:
            if st.button("Start AI Analysis"):
                patient_missing = validate_patient_info()
                image_missing = validate_uploads()
                if patient_missing:
                    st.warning("Please complete patient details before analysis: " + ", ".join(patient_missing))
                elif image_missing:
                    st.warning("Please upload all required images: " + ", ".join(image_missing))
                else:
                    try:
                        with st.spinner("Analyzing images and generating report..."):
                            eye_path = save_uploaded_image(st.session_state.eye_image, "eye")
                            nails_path = save_uploaded_image(st.session_state.nails_image, "nails")
                            tongue_path = save_uploaded_image(st.session_state.tongue_image, "tongue")

                            diagnosis_result = process_images(eye_path, nails_path, tongue_path)
                            comprehensive_diagnosis = diagnosis_result.get("comprehensive_diagnosis", "")
                            individual_analyses = diagnosis_result.get("individual_analyses", {})

                            severity = "moderate"
                            if "normal" in comprehensive_diagnosis.lower() or "healthy" in comprehensive_diagnosis.lower():
                                severity = "none"
                            elif "urgent" in comprehensive_diagnosis.lower() or "severe" in comprehensive_diagnosis.lower():
                                severity = "severe"

                            agent_1 = Agent1_ReportAndDiet()
                            agent_2 = Agent2_HospitalDoctor()

                            agent1_result = agent_1.execute(
                                diagnosis=comprehensive_diagnosis,
                                analyses={
                                    "eye": individual_analyses.get("eye", {}).get("analysis", ""),
                                    "nails": individual_analyses.get("nails", {}).get("analysis", ""),
                                    "tongue": individual_analyses.get("tongue", {}).get("analysis", ""),
                                },
                                condition_severity=severity,
                                patient_info={
                                    "name": st.session_state.patient_name,
                                    "age": st.session_state.patient_age,
                                    "sex": st.session_state.patient_sex,
                                    "location": st.session_state.patient_location,
                                    "medical_history": st.session_state.medical_history,
                                },
                            )

                            report = agent1_result.get("medical_report", {}).get("report", "")
                            diet_plan = agent1_result.get("diet_plan", {}).get("diet_plan", "")

                            agent2_result = agent_2.execute(
                                diagnosis=comprehensive_diagnosis,
                                location=st.session_state.patient_location,
                                patient_info={
                                    "name": st.session_state.patient_name,
                                    "age": st.session_state.patient_age,
                                    "sex": st.session_state.patient_sex,
                                    "location": st.session_state.patient_location,
                                },
                            )

                            st.session_state.analysis_results = {
                                "patient_name": st.session_state.patient_name,
                                "patient_age": st.session_state.patient_age,
                                "patient_sex": st.session_state.patient_sex,
                                "patient_email": st.session_state.patient_email,
                                "patient_location": st.session_state.patient_location,
                                "patient_phone": st.session_state.patient_phone,
                                "medical_history": st.session_state.medical_history,
                                "diagnosis": comprehensive_diagnosis,
                                "individual_analyses": individual_analyses,
                                "report": report,
                                "diet_plan": diet_plan,
                                "severity": severity,
                                "hospitals": agent2_result.get("hospitals", []),
                                "top_recommendation": agent2_result.get("top_recommendation", {}),
                                "timestamp": datetime.now().isoformat(),
                                "image_paths": {
                                    "eye": eye_path,
                                    "nails": nails_path,
                                    "tongue": tongue_path,
                                },
                            }
                            st.success("✅ Analysis completed successfully. Go to View Results to continue.")
                            st.session_state.current_page = "View Results"
                            st.experimental_rerun()
                    except Exception as exc:
                        logger.error(f"Analysis error: {exc}")
                        st.error(f"Error during analysis: {exc}")

elif page == "View Results":
    if not st.session_state.analysis_results:
        st.warning("No analysis results available yet. Please complete the Upload & Review flow first.")
    else:
        results = st.session_state.analysis_results
        st.subheader("📋 Analysis Results")

        cols = st.columns(4)
        cols[0].metric("Patient", results["patient_name"])
        cols[1].metric("Age", results["patient_age"])
        cols[2].metric("Sex", results["patient_sex"])
        cols[3].metric("Location", results["patient_location"])

        st.markdown("---")
        report_col, diet_col = st.columns(2)
        with report_col:
            if st.download_button(
                "Download Medical Report (PDF)",
                data=PDFReportGenerator.generate_medical_report_pdf(
                    {
                        "name": results["patient_name"],
                        "age": results["patient_age"],
                        "sex": results["patient_sex"],
                        "location": results["patient_location"],
                    },
                    results["diagnosis"],
                    results["report"],
                ),
                file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
            ):
                pass
        with diet_col:
            if results["diet_plan"]:
                if st.download_button(
                    "Download Diet Plan (PDF)",
                    data=PDFReportGenerator.generate_diet_plan_pdf(
                        {
                            "name": results["patient_name"],
                            "age": results["patient_age"],
                            "sex": results["patient_sex"],
                            "location": results["patient_location"],
                        },
                        results["diet_plan"],
                    ),
                    file_name=f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                ):
                    pass

        st.markdown("---")
        tabs = st.tabs(["Diagnosis", "Medical Report", "Diet Plan", "Doctors"])
        with tabs[0]:
            st.write(results["diagnosis"])
            st.markdown(
                f"**Severity:** {results.get('severity', 'Unknown')}"
            )

        with tabs[1]:
            st.write(results["report"] or "No medical report generated.")

        with tabs[2]:
            if results["diet_plan"]:
                st.write(results["diet_plan"])
            else:
                st.info("No diet plan generated for this case.")

        with tabs[3]:
            if results["top_recommendation"]:
                top = results["top_recommendation"]
                st.success("Top Recommendation")
                st.write(f"**Doctor:** {top.get('doctor', 'N/A')}")
                st.write(f"**Specialty:** {top.get('specialty', 'N/A')}")
                st.write(f"**Hospital:** {top.get('hospital', 'N/A')}")
            if results["hospitals"]:
                for idx, hospital in enumerate(results["hospitals"][:5], start=1):
                    with st.expander(f"Hospital {idx}: {hospital.get('name', 'N/A')}"):
                        st.write(f"**Address:** {hospital.get('address', 'N/A')}")
                        st.write(f"**Rating:** {hospital.get('rating', 'N/A')}")
                        st.write(f"**Info:** {hospital.get('info', 'N/A')}")

        st.markdown("---")
        st.subheader("📧 Email Results")
        if st.button("Send Results Email"):
            if not SENDER_EMAIL or not SENDER_PASSWORD:
                st.error("Email credentials are not configured in environment variables.")
            else:
                attachments = []
                report_pdf = PDFReportGenerator.generate_medical_report_pdf(
                    {
                        "name": results["patient_name"],
                        "age": results["patient_age"],
                        "sex": results["patient_sex"],
                        "location": results["patient_location"],
                    },
                    results["diagnosis"],
                    results["report"],
                )
                report_pdf.name = f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                attachments.append(report_pdf)

                if results["diet_plan"]:
                    diet_pdf = PDFReportGenerator.generate_diet_plan_pdf(
                        {
                            "name": results["patient_name"],
                            "age": results["patient_age"],
                            "sex": results["patient_sex"],
                            "location": results["patient_location"],
                        },
                        results["diet_plan"],
                    )
                    diet_pdf.name = f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    attachments.append(diet_pdf)

                body = f"Dear {results['patient_name']},\n\nYour AI medical analysis is ready. Please find the attached report and diet plan.\n\nDiagnosis:\n{results['diagnosis']}\n\nThank you,\nAI Medical Diagnostic System"
                success = EmailNotifier.send_email(results["patient_email"], "Your AI Diagnostic Results", body, attachments)
                if success:
                    st.success("✅ Results email sent successfully.")
                else:
                    st.error("❌ Failed to send email. Please check SMTP settings.")

elif page == "Book Appointment":
    if not st.session_state.analysis_results:
        st.warning("No analysis results available. Please complete the analysis first.")
    else:
        results = st.session_state.analysis_results
        st.subheader("📅 Book an Appointment")
        suitable_doctors = get_suitable_doctors(results["diagnosis"], results["patient_location"])
        if not suitable_doctors:
            st.error("No doctor recommendations available at the moment.")
        else:
            with st.form("appointment_form"):
                doctor_options = [
                    f"Dr. {doc['Doctor Name']} ({doc['Specialty']}) - {doc['City']}"
                    for doc in suitable_doctors
                ]
                selected = st.selectbox("Select Doctor *", doctor_options)
                selected_doctor = suitable_doctors[doctor_options.index(selected)]
                appointment_date = st.date_input("Preferred Date *", min_value=datetime.now().date(), value=datetime.now().date() + timedelta(days=1))
                appointment_time = st.selectbox(
                    "Preferred Time *",
                    ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"],
                )
                notes = st.text_area("Additional Notes (Optional)")
                submit_appointment = st.form_submit_button("Confirm Appointment")

                if submit_appointment:
                    appt = {
                        "doctor_name": selected_doctor["Doctor Name"],
                        "specialty": selected_doctor["Specialty"],
                        "hospital": selected_doctor["City"],
                        "date": appointment_date,
                        "time": datetime.strptime(appointment_time, "%I:%M %p").time(),
                        "notes": notes,
                    }
                    st.session_state.appointment_details = appt
                    st.success("✅ Appointment details saved.")
                    ics_content = create_ics_content(appt)
                    st.download_button(
                        "Download Calendar Invite (.ics)",
                        data=ics_content,
                        file_name=f"appointment_{appointment_date.strftime('%Y%m%d')}.ics",
                        mime="text/calendar",
                    )
                    if st.button("Send Appointment Confirmation Email"):
                        if not SENDER_EMAIL or not SENDER_PASSWORD:
                            st.error("Email credentials not configured.")
                        else:
                            attachments = []
                            medical_pdf = PDFReportGenerator.generate_medical_report_pdf(
                                {
                                    "name": results["patient_name"],
                                    "age": results["patient_age"],
                                    "sex": results["patient_sex"],
                                    "location": results["patient_location"],
                                },
                                results["diagnosis"],
                                results["report"],
                            )
                            medical_pdf.name = f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            attachments.append(medical_pdf)
                            if results["diet_plan"]:
                                diet_pdf = PDFReportGenerator.generate_diet_plan_pdf(
                                    {
                                        "name": results["patient_name"],
                                        "age": results["patient_age"],
                                        "sex": results["patient_sex"],
                                        "location": results["patient_location"],
                                    },
                                    results["diet_plan"],
                                )
                                diet_pdf.name = f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                attachments.append(diet_pdf)

                            ics_bytes = BytesIO(ics_content.encode("utf-8"))
                            ics_bytes.name = f"appointment_{appointment_date.strftime('%Y%m%d')}.ics"
                            attachments.append(ics_bytes)

                            body = (
                                f"Dear {results['patient_name']},\n\n"
                                f"Your appointment with Dr. {appt['doctor_name']} has been confirmed.\n"
                                f"Date: {appointment_date.strftime('%B %d, %Y')}\n"
                                f"Time: {appointment_time}\n"
                                f"Location: {appt['hospital']}\n\n"
                                "Please find the attached medical report, diet plan, and calendar invite.\n\n"
                                "Best regards,\nAI Medical Diagnostic System"
                            )
                            sent = EmailNotifier.send_email(results["patient_email"], "Appointment Confirmation", body, attachments)
                            if sent:
                                st.success("✅ Confirmation email sent.")
                            else:
                                st.error("❌ Failed to send confirmation email.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>AI Medical Diagnostic Dashboard · Use responsibly for diagnostic assistance only.</div>",
    unsafe_allow_html=True,
)
