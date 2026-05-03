"""
Advanced Features Module
PDF export, email notifications, batch processing, caching
"""

import logging
import smtplib
import os
import json
import pickle
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Optional, Any
from pathlib import Path
import asyncio
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Try to import PDF libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False
    logger.warning("⚠️  ReportLab not available - PDF export disabled")

# ========================
# PDF EXPORT
# ========================

class PDFExporter:
    """Generate PDF reports from medical analysis"""
    
    PDF_DIR = "reports/pdf"
    
    @staticmethod
    def init_pdf_dir():
        """Create PDF directory if not exists"""
        Path(PDFExporter.PDF_DIR).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_report_pdf(patient_name: str, age: int, sex: str,
                           diagnosis: str, severity: str,
                           medical_report: str, diet_plan: str,
                           doctors_info: dict = None, 
                           confidence: float = 0.0,
                           timestamp: str = None) -> Optional[str]:
        """Generate PDF report from medical analysis"""
        
        if not PDF_AVAILABLE:
            logger.warning("⚠️  PDF generation disabled - ReportLab not available")
            return None
        
        try:
            PDFExporter.init_pdf_dir()
            
            # Generate filename
            timestamp_str = timestamp or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            patient_name_safe = patient_name.replace(" ", "_").lower() if patient_name else "patient"
            pdf_filename = f"{PDFExporter.PDF_DIR}/{patient_name_safe}_{timestamp_str}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2e5fa3'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=10
            )
            
            # Title
            story.append(Paragraph("MEDICAL DIAGNOSTIC REPORT", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Patient Information
            story.append(Paragraph("PATIENT INFORMATION", heading_style))
            patient_data = [
                ['Name:', patient_name or 'Not Provided'],
                ['Age:', str(age) if age else 'Not Provided'],
                ['Sex:', sex or 'Not Provided'],
                ['Report Date:', datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Diagnosis Summary
            story.append(Paragraph("DIAGNOSIS SUMMARY", heading_style))
            diagnosis_data = [
                ['Primary Diagnosis:', diagnosis or 'Pending Analysis'],
                ['Severity Level:', severity or 'Unknown'],
                ['Confidence Score:', f"{confidence*100:.1f}%" if confidence else 'N/A'],
            ]
            
            diagnosis_table = Table(diagnosis_data, colWidths=[2*inch, 4*inch])
            diagnosis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(diagnosis_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Medical Report
            story.append(Paragraph("MEDICAL REPORT", heading_style))
            report_text = medical_report or "No report available"
            story.append(Paragraph(report_text, body_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Diet Plan
            story.append(Paragraph("PERSONALIZED DIET PLAN", heading_style))
            diet_text = diet_plan or "No diet plan available"
            story.append(Paragraph(diet_text, body_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Recommended Doctors/Hospitals
            if doctors_info:
                story.append(Paragraph("RECOMMENDED HEALTHCARE PROVIDERS", heading_style))
                story.append(Paragraph(str(doctors_info), body_style))
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            footer = Paragraph(
                "<i>This report is generated by AI Medical Diagnostic System. "
                "Consult with healthcare professionals for final diagnosis and treatment.</i>",
                styles['Italic']
            )
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            logger.info(f"✅ PDF Report generated: {pdf_filename}")
            
            return pdf_filename
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            return None

# ========================
# EMAIL NOTIFICATIONS
# ========================

class EmailNotifier:
    """Send email notifications"""
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    @staticmethod
    def _get_credentials():
        """Get Gmail credentials from environment (reload each time)"""
        # Reload .env to ensure latest values
        load_dotenv(override=True)
        
        sender = os.getenv("GMAIL_SENDER", "").strip()
        password = os.getenv("GMAIL_PASSWORD", "").strip()
        
        # Remove spaces from password (sometimes pasted with spaces)
        password = password.replace(" ", "")
        
        return sender, password
    
    @staticmethod
    def send_email(recipient: str, subject: str, body: str, 
                  html: str = None, attachments: list = None) -> bool:
        """Send email with optional attachments"""
        try:
            # Get fresh credentials
            sender, password = EmailNotifier._get_credentials()
            
            if not sender or not password:
                logger.warning(f"⚠️  Email credentials not configured. Sender: {sender if sender else 'EMPTY'}")
                return False
            
            logger.info(f"📧 Attempting to send email to {recipient} from {sender[:20]}...")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML if provided
            if html:
                msg.attach(MIMEText(html, 'html'))
            
            # Add attachments if provided
            if attachments:
                for attachment_path in attachments:
                    try:
                        if isinstance(attachment_path, str) and os.path.exists(attachment_path):
                            # Open file in binary mode
                            with open(attachment_path, 'rb') as attachment:
                                # Get filename
                                filename = os.path.basename(attachment_path)
                                
                                # Create MIME base object
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                                
                                # Encode as base64
                                encoders.encode_base64(part)
                                
                                # Add header with filename
                                part.add_header('Content-Disposition', 'attachment',
                                              filename=filename)
                                
                                # Attach to message
                                msg.attach(part)
                                logger.info(f"📎 Attached: {filename}")
                        else:
                            logger.warning(f"⚠️  Attachment file not found: {attachment_path}")
                    except Exception as e:
                        logger.error(f"❌ Error attaching file {attachment_path}: {e}")
            
            # Send
            with smtplib.SMTP(EmailNotifier.SMTP_SERVER, EmailNotifier.SMTP_PORT) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
            
            logger.info(f"✅ Email successfully sent to {recipient}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error(f"❌ Email authentication failed - check Gmail credentials")
            return False
        except Exception as e:
            logger.error(f"❌ Email send failed: {e}")
            return False
    
    @staticmethod
    def send_analysis_report(patient_email: str, patient_name: str, 
                            diagnosis: str, severity: str = "", 
                            medical_report: str = "", diet_plan: str = "",
                            hospitals: list = None, specialists: list = None,
                            pdf_path: str = None, confidence: float = 0.0) -> bool:
        """Send comprehensive analysis report via email"""
        subject = f"🏥 Your Medical Analysis Report - {diagnosis}"
        
        hospitals_text = ""
        if hospitals:
            hospitals_text = "\n\nRECOMMENDED HOSPITALS:\n" + "\n".join([f"• {h}" for h in hospitals[:5]])
        
        specialists_text = ""
        if specialists:
            specialists_text = "\n\nRECOMMENDED SPECIALISTS:\n" + ", ".join(specialists[:5])
        
        body = f"""
Dear {patient_name},

Your comprehensive medical analysis has been completed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 DIAGNOSIS SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Primary Diagnosis: {diagnosis}
Severity Level: {severity}
Confidence Score: {(confidence*100):.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 DETAILED MEDICAL REPORT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{medical_report if medical_report else 'No detailed report available.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥗 PERSONALIZED DIET PLAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{diet_plan if diet_plan else 'No diet plan available.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏥 HEALTHCARE PROVIDERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{hospitals_text if hospitals_text else 'No hospitals found for your location.'}

{specialists_text if specialists_text else 'No specialists recommended.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT NOTICE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This analysis is AI-powered and should NOT replace professional medical consultation.
Please consult with qualified healthcare professionals for proper diagnosis and treatment.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
🏥 AI Medical Diagnostic System
"""
        
        html_body = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 900px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea;">🏥 Your Medical Analysis Report</h2>
            <p>Dear <strong>{patient_name}</strong>,</p>
            
            <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #667eea; margin-top: 0;">🔍 Diagnosis Summary</h3>
                <p><strong>Primary Diagnosis:</strong> {diagnosis}</p>
                <p><strong>Severity Level:</strong> <span style="color: #f5576c; font-weight: bold;">{severity}</span></p>
                <p><strong>Confidence Score:</strong> {(confidence*100):.1f}%</p>
            </div>
            
            <div style="background: #fff8f0; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #667eea;">📋 Medical Report</h3>
                <p style="white-space: pre-wrap;">{medical_report if medical_report else 'No detailed report available.'}</p>
            </div>
            
            <div style="background: #f0fff4; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #667eea;">🥗 Diet Plan</h3>
                <p style="white-space: pre-wrap;">{diet_plan if diet_plan else 'No diet plan available.'}</p>
            </div>
            
            <div style="background: #f0f8ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #667eea;">🏥 Healthcare Providers</h3>
                {f'<p><strong>Hospitals:</strong></p><ul>{"".join([f"<li>{h}</li>" for h in hospitals[:5]])}</ul>' if hospitals else '<p>No hospitals found for your location.</p>'}
                {f'<p><strong>Specialists:</strong> {", ".join(specialists[:5])}</p>' if specialists else '<p>No specialists recommended.</p>'}
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
                <strong style="color: #856404;">⚠️ Important Notice:</strong>
                <p style="margin: 10px 0; color: #856404;">This analysis is AI-powered and should NOT replace professional medical consultation. Please consult with qualified healthcare professionals for proper diagnosis and treatment.</p>
            </div>
            
            <p style="color: #999;">Best regards,<br>🏥 AI Medical Diagnostic System</p>
        </div>
    </body>
</html>
"""
        
        # Prepare attachments
        attachments_list = []
        if pdf_path and os.path.exists(pdf_path):
            attachments_list.append(pdf_path)
            logger.info(f"📎 PDF attachment prepared: {pdf_path}")
        
        return EmailNotifier.send_email(patient_email, subject, body, html=html_body, 
                                       attachments=attachments_list if attachments_list else None)

# ========================
# BATCH PROCESSING
# ========================

class BatchProcessor:
    """Process multiple analyses in batch"""
    
    @staticmethod
    async def process_batch(analyses_data: list, process_func, 
                          progress_callback = None) -> dict:
        """Process multiple items in batch"""
        try:
            results = {
                "total": len(analyses_data),
                "completed": 0,
                "failed": 0,
                "errors": [],
                "results": []
            }
            
            for idx, item in enumerate(analyses_data):
                try:
                    if progress_callback:
                        await progress_callback(idx + 1, len(analyses_data))
                    
                    # Process item
                    result = await process_func(item) if asyncio.iscoroutinefunction(process_func) else process_func(item)
                    results["results"].append(result)
                    results["completed"] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Batch item failed: {e}")
                    results["failed"] += 1
                    results["errors"].append({
                        "item_index": idx,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return {"error": str(e)}

# ========================
# CACHING SYSTEM
# ========================

class CacheManager:
    """Simple caching system"""
    
    CACHE_DIR = "cache"
    CACHE_DURATION = 3600  # 1 hour
    
    @staticmethod
    def init_cache():
        """Initialize cache directory"""
        Path(CacheManager.CACHE_DIR).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_cache_key(prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        hash_obj = hashlib.sha256(data_str.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    @staticmethod
    def get_cache(key: str) -> Optional[Any]:
        """Get cached data"""
        try:
            cache_file = f"{CacheManager.CACHE_DIR}/{key}.cache"
            
            if not os.path.exists(cache_file):
                return None
            
            # Check if cache expired
            file_time = os.path.getmtime(cache_file)
            if datetime.utcnow().timestamp() - file_time > CacheManager.CACHE_DURATION:
                os.remove(cache_file)
                return None
            
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"✅ Cache hit: {key}")
            return data
            
        except Exception as e:
            logger.debug(f"⚠️  Cache read failed: {e}")
            return None
    
    @staticmethod
    def set_cache(key: str, data: Any) -> bool:
        """Cache data"""
        try:
            CacheManager.init_cache()
            cache_file = f"{CacheManager.CACHE_DIR}/{key}.cache"
            
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"✅ Cached: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache write failed: {e}")
            return False
    
    @staticmethod
    def clear_cache():
        """Clear all cache"""
        try:
            if os.path.exists(CacheManager.CACHE_DIR):
                for file in os.listdir(CacheManager.CACHE_DIR):
                    if file.endswith('.cache'):
                        os.remove(f"{CacheManager.CACHE_DIR}/{file}")
                logger.info("✅ Cache cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Cache clear failed: {e}")
            return False
    
    @staticmethod
    def get_cache_size() -> float:
        """Get cache size in MB"""
        try:
            total_size = 0
            if os.path.exists(CacheManager.CACHE_DIR):
                for file in os.listdir(CacheManager.CACHE_DIR):
                    if file.endswith('.cache'):
                        file_path = f"{CacheManager.CACHE_DIR}/{file}"
                        total_size += os.path.getsize(file_path)
            return total_size / (1024 * 1024)  # Convert to MB
        except:
            return 0

# ========================
# INITIALIZATION
# ========================

def init_features():
    """Initialize all features"""
    try:
        PDFExporter.init_pdf_dir()
        CacheManager.init_cache()
        logger.info("✅ Features initialized successfully")
    except Exception as e:
        logger.error(f"❌ Features initialization failed: {e}")

if __name__ == "__main__":
    init_features()
    print("✅ Features system initialized!")
