"""
Streamlit conversion of dashboard.html
Generates a multi-step medical diagnostic dashboard with image uploads,
review, results, appointment booking, email notifications, and calendar invites.
"""

import os
import html
import logging
import base64
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import streamlit as st
import pandas as pd
import smtplib
from email.mime.base import MIMEBase
from PIL import Image
import cv2
import numpy as np
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
    filename = getattr(uploaded_file, "name", None)
    extension = Path(filename).suffix if filename else ".jpg"
    if extension.lower() not in [".jpg", ".jpeg", ".png"]:
        extension = ".jpg"
    output_path = uploads_dir / f"{prefix}_{timestamp}{extension}"
    data = uploaded_file
    if not isinstance(uploaded_file, (bytes, bytearray)):
        data = get_uploaded_file_bytes(uploaded_file)
    with open(output_path, "wb") as f:
        f.write(data)
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
    has_eye = st.session_state.eye_image is not None or st.session_state.get("eye_image_bytes") is not None
    has_nails = st.session_state.nails_image is not None or st.session_state.get("nails_image_bytes") is not None
    has_tongue = st.session_state.tongue_image is not None or st.session_state.get("tongue_image_bytes") is not None
    
    if not has_eye:
        missing.append("Eye image")
    if not has_nails:
        missing.append("Nails image")
    if not has_tongue:
        missing.append("Tongue image")
    return missing


def get_uploaded_file_bytes(uploaded_file):
    try:
        if hasattr(uploaded_file, "getbuffer"):
            return uploaded_file.getbuffer()
        if hasattr(uploaded_file, "read"):
            uploaded_file.seek(0)
            return uploaded_file.read()
        return bytes(uploaded_file)
    except Exception as exc:
        logger.error(f"Error extracting bytes from uploaded file: {exc}")
        return None


def load_image_from_bytes(image_bytes):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as exc:
        logger.error(f"Error decoding image bytes: {exc}")
        return None


def detect_eye_features(image: np.ndarray) -> bool:
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade_path = cv2.data.haarcascades + "haarcascade_eye.xml"
        eye_cascade = cv2.CascadeClassifier(cascade_path)
        if eye_cascade.empty():
            return False
        detections = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return len(detections) > 0
    except Exception as exc:
        logger.error(f"Error detecting eyes: {exc}")
        return False


def detect_tongue_features(image: np.ndarray) -> bool:
    try:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        red_mask = ((h < 10) | (h > 160)) & (s > 90) & (v > 90)
        red_ratio = np.count_nonzero(red_mask) / red_mask.size
        average_red = np.mean(image[:, :, 2])
        red_area = red_ratio > 0.16
        bright_red = average_red > 115
        return red_area and bright_red
    except Exception as exc:
        logger.error(f"Error detecting tongue features: {exc}")
        return False


def detect_nails_features(image: np.ndarray) -> bool:
    try:
        if detect_eye_features(image):
            return False
        if detect_tongue_features(image):
            return False

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        image_area = image.shape[0] * image.shape[1]

        skin_mask = (h >= 0) & (h <= 35) & (s >= 10) & (s <= 140) & (v >= 50)
        nail_mask = (v >= 150) & (s <= 100) & ((h <= 25) | (h >= 160))
        pale_mask = (v >= 180) & (s <= 90) & (h <= 45)

        skin_area = np.count_nonzero(skin_mask)
        nail_area = np.count_nonzero(nail_mask)
        pale_area = np.count_nonzero(pale_mask)

        if skin_area / image_area < 0.06:
            return False

        if nail_area / image_area > 0.03:
            return True
        if pale_area / image_area > 0.025:
            return True

        combined_mask = np.uint8((nail_mask | pale_mask) * 255)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 0.005 * image_area:
                continue
            x, y, w, h_box = cv2.boundingRect(contour)
            if h_box == 0:
                continue
            aspect_ratio = float(w) / h_box
            if 0.25 < aspect_ratio < 5.0 and area / image_area > 0.015:
                valid_contours += 1

        if valid_contours >= 1:
            return True

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        edges = cv2.Canny(blurred, 50, 140)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        edge_contours = sum(1 for c in contours if cv2.contourArea(c) > 0.008 * image_area)

        return edge_contours >= 3
    except Exception as exc:
        logger.error(f"Error detecting nails features: {exc}")
        return False


def validate_body_part_image(uploaded_file, expected_part: str):
    if uploaded_file is None:
        return False, f"{expected_part.title()} image is missing."

    allowed_extensions = [".jpg", ".jpeg", ".png"]
    filename = getattr(uploaded_file, "name", None)
    extension = Path(filename).suffix.lower() if filename else ""
    if extension not in allowed_extensions:
        return False, f"{expected_part.title()} image must be JPG or PNG."

    image_bytes = get_uploaded_file_bytes(uploaded_file)
    if not image_bytes:
        return False, f"Could not read {expected_part} image data."

    image = load_image_from_bytes(image_bytes)
    if image is None:
        return False, f"{expected_part.title()} image is not a valid image file."

    lower_filename = filename.lower() if filename else ""
    if expected_part == "eye":
        if not detect_eye_features(image):
            if "eye" in lower_filename:
                return True, None
            return False, "Eye image does not appear to contain a human eye. Please upload a clear eye photo."
    elif expected_part == "tongue":
        if not detect_tongue_features(image):
            if "tongue" in lower_filename:
                return True, None
            return False, "Tongue image does not appear to contain a tongue. Please upload a clear tongue photo."
    elif expected_part == "nails":
        if not detect_nails_features(image):
            if "nail" in lower_filename:
                return True, None
            return False, "Nails image does not appear to contain nails. Please upload a nails photo only."

    return True, None


def validate_image_size():
    errors = []
    for field, label in [
        ("eye_image", "Eye image"),
        ("nails_image", "Nails image"),
        ("tongue_image", "Tongue image"),
    ]:
        uploaded = st.session_state.get(field)
        if uploaded is not None and hasattr(uploaded, "size"):
            if uploaded.size > 10 * 1024 * 1024:
                errors.append(f"{label} exceeds 10MB")
    return errors


# ========================
# UI helpers
# ========================

def render_progress_bar():
    step = st.session_state.current_step
    titles = ["Patient information", "Clinical images", "Review & analyze"]
    parts = []
    for index, title in enumerate(titles, start=1):
        if step == index:
            cls = "progress-step active"
        elif step > index:
            cls = "progress-step done"
        else:
            cls = "progress-step"
        parts.append(
            f'<div class="{cls}"><span class="progress-step-num">Step {index}</span>{title}</div>'
        )
    st.markdown(f'<div class="progress-row">{"".join(parts)}</div>', unsafe_allow_html=True)


def page_header():
    st.markdown(
        """
        <div class="app-header-shell">
            <div class="header-badge">Clinical decision support</div>
            <h1>AI Medical Diagnostic Dashboard</h1>
            <p class="tagline">Structured intake, multi-image analysis, and care coordination in one workflow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_card():
    summary = generate_result_summary()
    rows = "".join(
        f'<div class="summary-item"><strong>{label}</strong>{html.escape(str(value))}</div>'
        for label, value in summary.items()
    )
    st.markdown(
        f'<div class="card-panel"><h3 class="card-heading">Review summary</h3><div class="summary-grid">{rows}</div></div>',
        unsafe_allow_html=True,
    )


def top_command_bar():
    st.markdown(
        """
        <div class="top-bar">
            <span class="top-bar-brand">MedIntel · <span class="top-bar-dim">Command</span></span>
            <span class="top-bar-search">Search patients, studies, reports…</span>
            <span class="top-bar-actions">
                <span class="top-bar-pill">Notifications</span>
                <span class="top-bar-avatar">MS</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_analytics_strip(results: dict):
    ts_raw = results.get("timestamp") or ""
    ts_display = ts_raw[:19].replace("T", " · ") if ts_raw else "—"
    severity = html.escape(str(results.get("severity", "—")))
    diag_len = len(results.get("diagnosis") or "")
    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="kpi-card"><span class="kpi-label">Severity</span><span class="kpi-value">{severity}</span><span class="kpi-hint">Triage signal</span></div>
            <div class="kpi-card"><span class="kpi-label">Analysis depth</span><span class="kpi-value">{diag_len:,}</span><span class="kpi-hint">chars · fusion output</span></div>
            <div class="kpi-card"><span class="kpi-label">Last run</span><span class="kpi-value mono">{html.escape(ts_display)}</span><span class="kpi-hint">Session timestamp</span></div>
            <div class="kpi-card"><span class="kpi-label">Channels</span><span class="kpi-value">3 / 3</span><span class="kpi-hint">Eye · nails · tongue</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_notifications_and_timeline():
    st.markdown(
        """
        <div class="rail-stack">
            <div class="rail-card">
                <div class="rail-title">Notifications</div>
                <div class="rail-item"><span class="rail-dot"></span><strong>SLA</strong> Report review window active</div>
                <div class="rail-item"><span class="rail-dot violet"></span><strong>Models</strong> Vision encoder v2.4.1</div>
                <div class="rail-item muted"><span class="rail-dot off"></span><strong>Compliance</strong> No policy flags</div>
            </div>
            <div class="rail-card">
                <div class="rail-title">Recent activity</div>
                <div class="timeline">
                    <div class="tl-item"><span class="tl-time">09:42</span> Multimodal analysis completed</div>
                    <div class="tl-item"><span class="tl-time">09:18</span> PDF export generated</div>
                    <div class="tl-item"><span class="tl-time">08:55</span> Intake & imaging locked</div>
                </div>
            </div>
            <div class="chart-strip" style="margin-top:0.5rem;"><span class="c1"></span><span class="c2"></span><span class="c3"></span></div>
            <p style="font-size:0.72rem;color:#71717a;margin:0.35rem 0 0;">Signal blend · illustrative</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_copilot_sidebar():
    st.markdown('<div class="rail-title-text">AI assistant</div>', unsafe_allow_html=True)
    st.caption("Optional · prompts are not sent to a model in this build.")
    st.text_area(
        "Ask about this case or workflow",
        height=120,
        key="copilot_input",
        placeholder="e.g. Summarize key findings in patient-friendly language…",
        label_visibility="collapsed",
    )
    if st.button("Send to assistant", key="copilot_send", use_container_width=True):
        st.info("Wire this button to your LLM API when ready.")


# ========================
# Application layout
# ========================

st.set_page_config(
    page_title="AI Medical Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_state()

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-app: #09090b;
            --bg-elevated: rgba(24, 24, 27, 0.65);
            --border: rgba(255, 255, 255, 0.09);
            --text: #fafafa;
            --text-muted: #a1a1aa;
            --accent: #06b6d4;
            --accent-hover: #22d3ee;
            --accent-2: #8b5cf6;
            --accent-soft: rgba(6, 182, 212, 0.12);
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.45);
            --radius: 12px;
            --radius-lg: 16px;
            --font-base: 17px;
        }
        html {
            font-size: var(--font-base);
        }
        html, body,
        [data-testid="stAppViewContainer"] {
            font-family: 'Inter', 'DM Sans', ui-sans-serif, system-ui, sans-serif;
            color: var(--text);
        }
        .stApp {
            background: var(--bg-app);
            background-image:
                radial-gradient(ellipse 100% 80% at 50% -30%, rgba(59, 130, 246, 0.14), transparent),
                radial-gradient(ellipse 70% 50% at 100% 20%, rgba(139, 92, 246, 0.1), transparent),
                radial-gradient(ellipse 50% 40% at 0% 90%, rgba(6, 182, 212, 0.08), transparent);
        }
        [data-testid="stHeader"] {
            background: rgba(9, 9, 11, 0.85) !important;
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
        }
        .main .block-container {
            padding: 1.5rem 1.75rem 3rem 1.75rem;
            max-width: 1320px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(12, 12, 16, 0.98) 0%, rgba(24, 24, 27, 0.95) 100%) !important;
            border-right: 1px solid var(--border);
            min-width: 15rem !important;
            backdrop-filter: blur(20px);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem;
            padding-left: 1.25rem;
            padding-right: 1.25rem;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            line-height: 1.45 !important;
            color: var(--text) !important;
            padding: 0.35rem 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] > div {
            gap: 0.5rem !important;
        }
        .main .stMarkdown h1 { font-size: 1.85rem !important; font-weight: 700; letter-spacing: -0.02em; color: var(--text); }
        .main .stMarkdown h2 { font-size: 1.45rem !important; font-weight: 600; color: var(--text); }
        .main .stMarkdown h3 { font-size: 1.2rem !important; font-weight: 600; color: var(--text); }
        .main .stMarkdown p, .main .stMarkdown li {
            font-size: 1.05rem !important;
            line-height: 1.65;
            color: var(--text);
        }
        .stCaption, [data-testid="stCaption"] {
            font-size: 0.95rem !important;
            color: var(--text-muted) !important;
        }
        .stTextInput label, .stNumberInput label, .stSelectbox label,
        .stTextArea label, .stDateInput label, .stFileUploader label,
        .stMultiSelect label {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: var(--text) !important;
        }
        .stTextInput input, .stTextArea textarea, .stNumberInput input,
        .stDateInput input {
            font-size: 1.02rem !important;
            border-radius: var(--radius) !important;
            background: rgba(255, 255, 255, 0.04) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
            background: rgba(255, 255, 255, 0.05) !important;
            border-color: var(--border) !important;
            color: var(--text) !important;
        }
        [data-testid="stFileUploader"] section {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px dashed rgba(255, 255, 255, 0.15) !important;
            border-radius: var(--radius) !important;
        }
        .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
            border-radius: var(--radius) !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding: 0.65rem 1.15rem !important;
            border: none !important;
            transition: background 0.15s ease, box-shadow 0.15s ease;
        }
        .stButton > button, .stFormSubmitButton > button {
            background: linear-gradient(135deg, #0891b2 0%, #2563eb 55%, #7c3aed 100%) !important;
            color: #fff !important;
            box-shadow: 0 4px 20px rgba(6, 182, 212, 0.25);
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            filter: brightness(1.08);
            box-shadow: 0 6px 28px rgba(139, 92, 246, 0.25);
        }
        .stDownloadButton > button {
            background: linear-gradient(135deg, #27272a 0%, #18181b 100%) !important;
            color: #fafafa !important;
            border: 1px solid var(--border) !important;
        }
        .stDownloadButton > button:hover {
            border-color: rgba(6, 182, 212, 0.45) !important;
            box-shadow: 0 0 24px rgba(6, 182, 212, 0.15);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
            background: transparent;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: var(--radius) var(--radius) 0 0;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.55rem 1rem;
            color: var(--text-muted) !important;
        }
        .stTabs [aria-selected="true"] {
            color: var(--accent-hover) !important;
            border-bottom: 2px solid var(--accent) !important;
        }
        [data-testid="stMetric"] {
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1rem 1.15rem;
            box-shadow: var(--shadow-sm);
            backdrop-filter: blur(12px);
        }
        [data-testid="stMetric"] label {
            font-size: 0.8rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted) !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            color: var(--text) !important;
        }
        .stAlert { border-radius: var(--radius) !important; font-size: 1rem !important; }
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1.02rem;
            color: var(--text) !important;
            background: rgba(255, 255, 255, 0.03) !important;
        }
        .app-header-shell {
            background: linear-gradient(125deg, rgba(6, 182, 212, 0.25) 0%, rgba(37, 99, 235, 0.2) 40%, rgba(124, 58, 237, 0.22) 100%),
                linear-gradient(180deg, #18181b 0%, #0c0c0f 100%);
            border-radius: var(--radius-lg);
            padding: 2rem 2.25rem;
            color: #f8fafc;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-md);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
        }
        .app-header-shell h1 {
            margin: 0;
            font-size: 2.05rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.2;
        }
        .app-header-shell .tagline {
            margin: 0.65rem 0 0;
            font-size: 1.12rem;
            line-height: 1.6;
            opacity: 0.95;
            max-width: 44rem;
            font-weight: 400;
        }
        .header-badge {
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            background: rgba(255, 255, 255, 0.14);
            padding: 0.4rem 0.75rem;
            border-radius: 999px;
            margin-bottom: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.22);
        }
        .section-title {
            font-size: 1.55rem;
            font-weight: 700;
            color: var(--text);
            margin: 0 0 0.45rem 0;
            letter-spacing: -0.02em;
        }
        .section-subtitle {
            font-size: 1.08rem;
            color: var(--text-muted);
            margin: 0 0 1.5rem 0;
            line-height: 1.6;
        }
        .section-label {
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin: 0 0 0.75rem 0;
        }
        .card-panel {
            background: var(--bg-elevated);
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            padding: 1.5rem 1.65rem;
            box-shadow: var(--shadow-sm);
            margin-bottom: 1.25rem;
            backdrop-filter: blur(16px);
        }
        .card-heading {
            margin: 0 0 1.1rem 0;
            font-size: 1.28rem;
            font-weight: 600;
            color: var(--text);
        }
        .progress-row {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        .progress-step {
            flex: 1;
            min-width: 140px;
            padding: 0.9rem 1rem;
            border-radius: var(--radius);
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            text-align: center;
            font-size: 0.98rem;
            font-weight: 500;
            color: var(--text-muted);
            line-height: 1.4;
            box-shadow: var(--shadow-sm);
        }
        .progress-step-num {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            opacity: 0.85;
            margin-bottom: 0.4rem;
        }
        .progress-step.active {
            border-color: rgba(6, 182, 212, 0.55);
            background: rgba(6, 182, 212, 0.1);
            color: #e0f2fe;
            font-weight: 600;
        }
        .progress-step.done {
            color: #67e8f9;
            border-color: rgba(6, 182, 212, 0.35);
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
            gap: 0.65rem 1.1rem;
        }
        .summary-item {
            font-size: 1rem;
            line-height: 1.45;
            color: var(--text);
        }
        .summary-item strong {
            display: block;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
            margin-bottom: 0.2rem;
        }
        .upload-callout {
            background: rgba(6, 182, 212, 0.1);
            border: 1px solid rgba(6, 182, 212, 0.28);
            border-radius: var(--radius);
            padding: 0.55rem 0.85rem;
            font-size: 0.95rem;
            font-weight: 600;
            color: #a5f3fc;
            margin-bottom: 0.5rem;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.1rem 1.75rem;
        }
        @media (max-width: 720px) {
            .feature-grid { grid-template-columns: 1fr; }
        }
        .feature-item {
            display: flex;
            gap: 0.85rem;
            align-items: flex-start;
            font-size: 1.05rem;
            color: var(--text-muted);
            line-height: 1.55;
        }
        .feature-item strong {
            font-size: 1.05rem !important;
            color: var(--text) !important;
        }
        .feature-icon {
            flex-shrink: 0;
            width: 2rem;
            height: 2rem;
            border-radius: 10px;
            background: rgba(139, 92, 246, 0.15);
            color: #c4b5fd;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
            font-weight: 700;
        }
        .home-tile {
            box-sizing: border-box;
            min-height: 22rem;
        }
        .home-tile--capabilities {
            display: flex;
            flex-direction: column;
        }
        .home-tile--capabilities .feature-grid {
            flex: 1;
            align-content: center;
        }
        .home-tile--session {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        .home-intro-text {
            color: var(--text-muted);
            font-size: 1.08rem;
            line-height: 1.6;
            margin: 0 0 0.25rem 0;
        }
        [data-testid="stHorizontalBlock"]:has(.home-tile) {
            align-items: stretch !important;
        }
        [data-testid="stHorizontalBlock"]:has(.home-tile) > [data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
        }
        [data-testid="stHorizontalBlock"]:has(.home-tile) > [data-testid="column"] [data-testid="stVerticalBlock"] {
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.home-tile) > [data-testid="column"]:nth-child(1) .home-tile {
            flex: 1 1 auto;
            min-height: 24rem;
        }
        [data-testid="stHorizontalBlock"]:has(.home-tile) > [data-testid="column"]:nth-child(2) .home-tile--session {
            flex: 1 1 auto;
        }
        [data-testid="stHorizontalBlock"]:has(.home-tile) > [data-testid="column"]:nth-child(2) .stButton {
            margin-top: auto !important;
            padding-top: 0.75rem !important;
        }
        .sidebar-brand {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-muted);
            margin-bottom: 0.35rem;
        }
        .sidebar-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 1rem;
            line-height: 1.3;
        }
        .nav-heading-sidebar {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text);
            margin: 0.5rem 0 0.75rem 0;
        }
        .app-footer {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.95rem;
            line-height: 1.55;
            padding: 1.5rem 1rem 0.5rem;
            margin-top: 2rem;
            border-top: 1px solid var(--border);
        }
        .muted-inline { color: var(--text-muted) !important; }
        .top-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
            padding: 0.65rem 1rem;
            margin-bottom: 1rem;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(14px);
            font-size: 0.85rem;
        }
        .top-bar-brand { font-weight: 600; color: var(--text); }
        .top-bar-dim { color: var(--text-muted); font-weight: 500; }
        .top-bar-search {
            flex: 1;
            min-width: 160px;
            color: var(--text-muted);
            padding: 0.35rem 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(0,0,0,0.25);
            font-size: 0.8rem;
        }
        .top-bar-actions { display: flex; align-items: center; gap: 0.5rem; }
        .top-bar-pill {
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.1);
            color: var(--text-muted);
            font-size: 0.72rem;
            font-weight: 600;
        }
        .top-bar-avatar {
            width: 2rem;
            height: 2rem;
            border-radius: 10px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            font-weight: 800;
            color: #fff;
        }
        .kpi-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }
        .kpi-card {
            padding: 1rem 1.1rem;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(12px);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .kpi-card:hover {
            border-color: rgba(6, 182, 212, 0.35);
            box-shadow: 0 0 24px rgba(6, 182, 212, 0.08);
        }
        .kpi-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
        .kpi-value { display: block; font-size: 1.25rem; font-weight: 700; color: var(--text); margin-top: 0.35rem; }
        .kpi-hint { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.25rem; }
        .kpi-value.mono { font-family: ui-monospace, monospace; font-size: 0.85rem; font-weight: 600; }
        .rail-stack { display: flex; flex-direction: column; gap: 0.75rem; }
        .rail-card {
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1rem 1.1rem;
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(14px);
        }
        .rail-title { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #a5b4fc; margin-bottom: 0.65rem; }
        .rail-title-text { font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem; }
        .rail-item { font-size: 0.82rem; color: #d4d4d8; margin-bottom: 0.5rem; display: flex; gap: 0.5rem; align-items: flex-start; line-height: 1.4; }
        .rail-item.muted { color: var(--text-muted); }
        .rail-item strong { color: #e0e7ff; font-weight: 600; }
        .rail-dot { width: 6px; height: 6px; border-radius: 999px; background: #22d3ee; margin-top: 0.35rem; flex-shrink: 0; box-shadow: 0 0 8px rgba(34,211,238,0.6); }
        .rail-dot.violet { background: #a78bfa; box-shadow: 0 0 8px rgba(167,139,250,0.5); }
        .rail-dot.off { background: #52525b; box-shadow: none; }
        .timeline { display: flex; flex-direction: column; gap: 0.65rem; }
        .tl-item { font-size: 0.82rem; color: #d4d4d8; padding-left: 0.5rem; border-left: 2px solid rgba(6,182,212,0.35); }
        .tl-time { font-family: ui-monospace, monospace; font-size: 0.68rem; color: #22d3ee; margin-right: 0.35rem; }
        .chart-strip {
            display: flex;
            height: 6px;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 0.75rem;
            opacity: 0.9;
        }
        .chart-strip span { flex: 1; }
        .chart-strip .c1 { background: linear-gradient(90deg, #06b6d4, #3b82f6); }
        .chart-strip .c2 { background: linear-gradient(90deg, #3b82f6, #8b5cf6); }
        .chart-strip .c3 { background: linear-gradient(90deg, #8b5cf6, #22d3ee); }
        section.main [data-testid="stMarkdownContainer"] p { color: #d4d4d8 !important; }
        section.main [data-testid="stMarkdownContainer"] li { color: #d4d4d8 !important; }
        hr { border: none; border-top: 1px solid var(--border); margin: 1.75rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    '<div class="sidebar-brand">Workspace</div><div class="sidebar-title">Clinical workflow</div>'
    '<div class="nav-heading-sidebar">Navigation</div>',
    unsafe_allow_html=True,
)
pages = ["Home", "Upload & Review", "View Results"]
current_page = st.session_state.get("current_page", "Home")
page = st.sidebar.radio(
    "Section",
    pages,
    index=pages.index(current_page),
    label_visibility="collapsed",
)

if page != st.session_state.current_page:
    st.session_state.current_page = page

top_command_bar()
page_header()

if page == "Home":
    st.markdown("<div class='section-title'>Welcome</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Digital intake, AI-assisted image review, and coordinated follow-up in one place.</div>",
        unsafe_allow_html=True,
    )
    intro_col, action_col = st.columns([2, 1])
    with intro_col:
        st.markdown(
            """
            <div class="card-panel home-tile home-tile--capabilities">
                <h3 class="card-heading">Capabilities</h3>
                <div class="feature-grid">
                    <div class="feature-item"><span class="feature-icon">1</span><span><strong>Intake</strong><br/>Structured demographics, history, and contact details.</span></div>
                    <div class="feature-item"><span class="feature-icon">2</span><span><strong>Imaging</strong><br/>Eye, nails, and tongue capture with quality guidance.</span></div>
                    <div class="feature-item"><span class="feature-icon">3</span><span><strong>Analysis</strong><br/>Diagnostics, report, and diet guidance for review.</span></div>
                    <div class="feature-item"><span class="feature-icon">4</span><span><strong>Coordination</strong><br/>Doctors, booking, calendar invite, and email delivery.</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with action_col:
        st.markdown(
            """
            <div class="card-panel home-tile home-tile--session" style="text-align:center;">
                <h3 class="card-heading">Begin session</h3>
                <p class="home-intro-text">Continue to intake and imaging. You can review everything before analysis runs.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start new diagnosis", use_container_width=True):
            st.session_state.current_page = "Upload & Review"
            st.rerun()

elif page == "Upload & Review":
    st.markdown("<div class='section-title'>Patient information & imaging</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Complete intake, upload clinical images, then review before analysis.</div>",
        unsafe_allow_html=True,
    )
    render_progress_bar()

    if st.session_state.current_step == 1:
        with st.form("patient_info_form"):
            st.markdown(
                "<div class='card-panel'><h3 class='card-heading'>Patient intake</h3><p class='muted-inline' style='margin:0 0 1.25rem;font-size:1.05rem;line-height:1.6;'>Accurate demographics and history improve recommendations.</p>",
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                patient_name = st.text_input("Full Name *", value=st.session_state.patient_name or "", placeholder="John Doe")
                patient_age = st.number_input("Age *", min_value=1, max_value=120, value=st.session_state.patient_age or 30)
                patient_sex = st.selectbox("Sex *", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.patient_sex) if st.session_state.patient_sex in ["Male", "Female", "Other"] else 0)
            with col2:
                patient_location = st.text_input("Location/City *", value=st.session_state.patient_location or "", placeholder="New York, NY")
                patient_email = st.text_input("Email Address *", value=st.session_state.patient_email or "", placeholder="you@example.com")
                patient_phone = st.text_input("Phone", value=st.session_state.patient_phone or "", placeholder="Optional")
            medical_history = st.text_area("Medical History", value=st.session_state.medical_history or "", height=150, placeholder="Describe any known conditions, allergies, or symptoms.")
            st.markdown("</div>", unsafe_allow_html=True)

            submit = st.form_submit_button("Continue to imaging →")
            if submit:
                st.session_state.patient_name = patient_name.strip()
                st.session_state.patient_age = patient_age
                st.session_state.patient_sex = patient_sex
                st.session_state.patient_location = patient_location.strip()
                st.session_state.patient_email = patient_email.strip()
                st.session_state.patient_phone = patient_phone.strip()
                st.session_state.medical_history = medical_history.strip()

                missing = validate_patient_info()
                if missing:
                    st.warning("Please complete the required patient details: " + ", ".join(missing))
                else:
                    st.session_state.current_step = 2
                    st.rerun()

    elif st.session_state.current_step == 2:
        st.markdown(
            "<div class='card-panel'><h3 class='card-heading'>Clinical images</h3><p class='muted-inline' style='margin:0 0 1.25rem;font-size:1.05rem;line-height:1.6;'>Well-lit, in-focus photos. All three views are required.</p>",
            unsafe_allow_html=True,
        )
        upload_cols = st.columns(3)
        with upload_cols[0]:
            st.markdown('<div class="upload-callout">Eye</div>', unsafe_allow_html=True)
            st.file_uploader("Upload eye image", type=["jpg", "jpeg", "png"], key="eye_image", help="Upload a clear eye photo")
            if st.session_state.eye_image:
                st.image(st.session_state.eye_image, caption="Eye preview", use_container_width=True)
                st.write(f"Uploaded: {st.session_state.eye_image.name}")
        with upload_cols[1]:
            st.markdown('<div class="upload-callout">Nails</div>', unsafe_allow_html=True)
            st.file_uploader("Upload nails image", type=["jpg", "jpeg", "png"], key="nails_image", help="Upload a clear nails photo")
            if st.session_state.nails_image:
                st.image(st.session_state.nails_image, caption="Nails preview", use_container_width=True)
                st.write(f"Uploaded: {st.session_state.nails_image.name}")
        with upload_cols[2]:
            st.markdown('<div class="upload-callout">Tongue</div>', unsafe_allow_html=True)
            st.file_uploader("Upload tongue image", type=["jpg", "jpeg", "png"], key="tongue_image", help="Upload a clear tongue photo")
            if st.session_state.tongue_image:
                st.image(st.session_state.tongue_image, caption="Tongue preview", use_container_width=True)
                st.write(f"Uploaded: {st.session_state.tongue_image.name}")

        if st.session_state.eye_image:
            st.session_state.eye_image_bytes = get_uploaded_file_bytes(st.session_state.eye_image)
        if st.session_state.nails_image:
            st.session_state.nails_image_bytes = get_uploaded_file_bytes(st.session_state.nails_image)
        if st.session_state.tongue_image:
            st.session_state.tongue_image_bytes = get_uploaded_file_bytes(st.session_state.tongue_image)

        file_errors = validate_image_size()
        image_validation_errors = []
        if st.session_state.eye_image:
            valid, message = validate_body_part_image(st.session_state.eye_image, "eye")
            if not valid and message:
                image_validation_errors.append(message)
        if st.session_state.nails_image:
            valid, message = validate_body_part_image(st.session_state.nails_image, "nails")
            if not valid and message:
                image_validation_errors.append(message)
        if st.session_state.tongue_image:
            valid, message = validate_body_part_image(st.session_state.tongue_image, "tongue")
            if not valid and message:
                image_validation_errors.append(message)

        if file_errors:
            for error in file_errors:
                st.error(error)
        if image_validation_errors:
            for error in image_validation_errors:
                st.error(error)

        st.caption("Maximum 10 MB per image. Bright, steady shots produce more reliable analysis.")
        nav_cols = st.columns([1, 1])
        with nav_cols[0]:
            if st.button("Back", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        with nav_cols[1]:
            if st.button("Continue to review →", use_container_width=True):
                missing = validate_uploads()
                patient_missing = validate_patient_info()
                if patient_missing:
                    st.warning("Please complete the patient information before continuing: " + ", ".join(patient_missing))
                elif missing:
                    st.warning("Please upload the following images: " + ", ".join(missing))
                elif file_errors or image_validation_errors:
                    st.warning("Please fix the image upload issues before continuing.")
                else:
                    st.session_state.current_step = 3
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_step == 3:
        render_summary_card()
        if st.session_state.eye_image or st.session_state.nails_image or st.session_state.tongue_image or st.session_state.get("eye_image_bytes") or st.session_state.get("nails_image_bytes") or st.session_state.get("tongue_image_bytes"):
            preview_cols = st.columns(3)
            with preview_cols[0]:
                if st.session_state.eye_image:
                    st.subheader("Eye Preview")
                    st.image(st.session_state.eye_image, use_container_width=True)
                elif st.session_state.get("eye_image_bytes"):
                    st.subheader("Eye Preview")
                    eye_img = load_image_from_bytes(st.session_state.get("eye_image_bytes"))
                    if eye_img is not None:
                        st.image(eye_img, channels="BGR", use_container_width=True)
            with preview_cols[1]:
                if st.session_state.nails_image:
                    st.subheader("Nails Preview")
                    st.image(st.session_state.nails_image, use_container_width=True)
                elif st.session_state.get("nails_image_bytes"):
                    st.subheader("Nails Preview")
                    nails_img = load_image_from_bytes(st.session_state.get("nails_image_bytes"))
                    if nails_img is not None:
                        st.image(nails_img, channels="BGR", use_container_width=True)
            with preview_cols[2]:
                if st.session_state.tongue_image:
                    st.subheader("Tongue Preview")
                    st.image(st.session_state.tongue_image, use_container_width=True)
                elif st.session_state.get("tongue_image_bytes"):
                    st.subheader("Tongue Preview")
                    tongue_img = load_image_from_bytes(st.session_state.get("tongue_image_bytes"))
                    if tongue_img is not None:
                        st.image(tongue_img, channels="BGR", use_container_width=True)

        st.warning("For decision support only. Does not replace evaluation by a licensed clinician.")
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("Back", use_container_width=True, key="review_back"):
                st.session_state.current_step = 2
                st.rerun()
        with cols[1]:
            if st.button("Run analysis", use_container_width=True, key="run_analysis"):
                patient_missing = validate_patient_info()
                image_missing = validate_uploads()
                validation_errors = []
                
                eye_obj = st.session_state.eye_image or st.session_state.get("eye_image_bytes")
                nails_obj = st.session_state.nails_image or st.session_state.get("nails_image_bytes")
                tongue_obj = st.session_state.tongue_image or st.session_state.get("tongue_image_bytes")
                
                if eye_obj and st.session_state.eye_image:
                    valid, message = validate_body_part_image(st.session_state.eye_image, "eye")
                    if not valid and message:
                        validation_errors.append(message)
                if nails_obj and st.session_state.nails_image:
                    valid, message = validate_body_part_image(st.session_state.nails_image, "nails")
                    if not valid and message:
                        validation_errors.append(message)
                if tongue_obj and st.session_state.tongue_image:
                    valid, message = validate_body_part_image(st.session_state.tongue_image, "tongue")
                    if not valid and message:
                        validation_errors.append(message)

                if patient_missing:
                    st.warning("Please complete patient details before analysis: " + ", ".join(patient_missing))
                elif image_missing:
                    st.warning("Please upload all required images: " + ", ".join(image_missing))
                elif validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    try:
                        with st.spinner("Analyzing images and generating report..."):
                            eye_path = save_uploaded_image(
                                eye_obj,
                                "eye",
                            )
                            nails_path = save_uploaded_image(
                                nails_obj,
                                "nails",
                            )
                            tongue_path = save_uploaded_image(
                                tongue_obj,
                                "tongue",
                            )

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
                            st.rerun()
                    except Exception as exc:
                        logger.error(f"Analysis error: {exc}")
                        st.error(f"Error during analysis: {exc}")

elif page == "View Results":
    if not st.session_state.analysis_results:
        st.warning("No analysis results available yet. Please complete the Upload & Review flow first.")
    else:
        results = st.session_state.analysis_results
        st.markdown("<div class='section-title'>Analysis results</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Review outputs, export documents, and arrange follow-up.</div>",
            unsafe_allow_html=True,
        )

        render_overview_analytics_strip(results)
        cols = st.columns(4)
        cols[0].metric("Patient", results["patient_name"])
        cols[1].metric("Age", results["patient_age"])
        cols[2].metric("Sex", results["patient_sex"])
        cols[3].metric("Location", results["patient_location"])

        st.markdown("<div class='section-label'>Exports</div>", unsafe_allow_html=True)
        report_col, diet_col = st.columns(2)
        with report_col:
            if st.download_button(
                "Medical report (PDF)",
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
                key="dl_report_pdf",
            ):
                pass
        with diet_col:
            if results["diet_plan"]:
                if st.download_button(
                    "Diet plan (PDF)",
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
                    key="dl_diet_pdf",
                ):
                    pass

        st.markdown("---")
        tabs = st.tabs(["Diagnosis", "Report", "Diet", "Care network"])
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
                st.success("Recommended match")
                st.write(f"**Physician:** {top.get('doctor', 'N/A')}")
                st.write(f"**Specialty:** {top.get('specialty', 'N/A')}")
                st.write(f"**Facility:** {top.get('hospital', 'N/A')}")
            if results["hospitals"]:
                for idx, hospital in enumerate(results["hospitals"][:5], start=1):
                    with st.expander(f"Hospital {idx}: {hospital.get('name', 'N/A')}"):
                        st.write(f"**Address:** {hospital.get('address', 'N/A')}")
                        st.write(f"**Rating:** {hospital.get('rating', 'N/A')}")
                        st.write(f"**Info:** {hospital.get('info', 'N/A')}")

        st.markdown("---")
        st.markdown("<div class='section-title'>Schedule appointment</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Select a provider and time; save details and download a calendar file if needed.</div>",
            unsafe_allow_html=True,
        )
        suitable_doctors = get_suitable_doctors(results["diagnosis"], results["patient_location"])
        if not suitable_doctors:
            st.warning("No doctor recommendations available at the moment.")
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
                submit_appointment = st.form_submit_button("Confirm appointment")

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

            # st.download_button is not allowed inside st.form(); render after the form closes.
            if st.session_state.get("appointment_details"):
                appt_saved = st.session_state.appointment_details
                ics_content = create_ics_content(appt_saved)
                st.download_button(
                    "Calendar invite (.ics)",
                    data=ics_content,
                    file_name=f"appointment_{appt_saved['date'].strftime('%Y%m%d')}.ics",
                    mime="text/calendar",
                    key="download_appointment_ics",
                )

        st.markdown("---")
        st.markdown("<div class='section-title'>Email delivery</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Send reports and optional appointment details to the patient email on file.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Send results & appointment by email", use_container_width=True):
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
                
                if st.session_state.appointment_details:
                    appt = st.session_state.appointment_details
                    ics_content = create_ics_content(appt)
                    ics_bytes = BytesIO(ics_content.encode("utf-8"))
                    ics_bytes.name = f"appointment_{appt['date'].strftime('%Y%m%d')}.ics"
                    attachments.append(ics_bytes)
                    
                    body = (
                        f"Dear {results['patient_name']},\n\n"
                        f"Your AI medical analysis is ready, and your appointment has been confirmed.\n\n"
                        f"Appointment Details:\n"
                        f"Doctor: Dr. {appt['doctor_name']}\n"
                        f"Specialty: {appt['specialty']}\n"
                        f"Date: {appt['date'].strftime('%B %d, %Y')}\n"
                        f"Time: {appt['time'].strftime('%I:%M %p')}\n"
                        f"Location: {appt['hospital']}\n\n"
                        f"Diagnosis:\n{results['diagnosis']}\n\n"
                        f"Please find the attached medical report, diet plan, and calendar invite.\n\n"
                        f"Best regards,\nAI Medical Diagnostic System"
                    )
                
                success = EmailNotifier.send_email(results["patient_email"], "Your AI Diagnostic Results & Appointment", body, attachments)
                if success:
                    st.success("✅ Results and appointment email sent successfully.")
                else:
                    st.error("❌ Failed to send email. Please check SMTP settings.")

        dock1, dock2 = st.columns(2)
        with dock1:
            render_notifications_and_timeline()
        with dock2:
            render_copilot_sidebar()


st.markdown("---")
st.markdown(
    '<div class="app-footer">AI Medical Diagnostic Dashboard · For clinical decision support only · Not a substitute for professional care.</div>',
    unsafe_allow_html=True,
)
