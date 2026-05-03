# 🏥 AI Medical Diagnostic System - Streamlit Interface

## Overview

This is a modern, user-friendly Streamlit application for the AI Medical Diagnostic System. It provides a complete workflow for:
1. **Upload & Analyze**: Upload medical images (eye, nails, tongue) for AI-powered diagnosis
2. **View Results**: See detailed analysis, medical reports, and personalized diet plans
3. **Book Appointment**: Schedule appointments with recommended doctors and receive email confirmations

## Features

✅ **Multi-Image Analysis**: Analyze eye, nails, and tongue images for comprehensive health assessment
✅ **AI-Powered Diagnosis**: Uses advanced vision agents and LLMs for accurate diagnosis
✅ **Medical Reports**: Generates professional medical reports based on analysis
✅ **Diet Plans**: Personalized nutrition recommendations based on diagnosis
✅ **Doctor Finder**: Automatically finds suitable doctors and nearest hospitals
✅ **Appointment Booking**: Schedule appointments with recommended doctors
✅ **Email Notifications**: Sends confirmation emails with appointment details
✅ **Responsive UI**: Beautiful, intuitive interface built with Streamlit

## Requirements

- Python 3.8+
- Virtual environment (recommended)
- API Keys:
  - **GROQ API Key** (free, recommended) OR **Anthropic Claude API Key**
  - **Serper API Key** (for hospital/doctor search)
  - **Email credentials** (Gmail SMTP recommended)

## Installation & Setup

### 1. Install Streamlit and Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\activate.bat  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or edit `.env` file in the project root:

```env
# LLM Configuration
USE_GROQ=true
GROQ_API_KEY=gsk_your_groq_api_key_here
# OR for Anthropic Claude:
# ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# Search Configuration
SERPER_API_KEY=your_serper_api_key_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password

# App Configuration
DEBUG_MODE=true
```

### 3. Get API Keys

#### Option A: GROQ (Free, Recommended)
1. Go to https://console.groq.com/keys
2. Sign up for free account
3. Generate API key
4. Add to `.env`

#### Option B: Anthropic Claude
1. Go to https://console.anthropic.com
2. Create account and billing setup
3. Generate API key
4. Add to `.env`

#### For Hospital Search (Serper)
1. Go to https://serper.dev
2. Sign up (free tier available)
3. Generate API key
4. Add to `.env`

#### For Email Notifications (Gmail)
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password in `.env` (not your regular Gmail password)

## Running the Application

### Quick Start

```bash
# Windows
run_streamlit.bat

# Linux/Mac
bash run_streamlit.sh
```

### Manual Start

```bash
# Activate virtual environment
.\venv\Scripts\activate.bat  # Windows

# Run Streamlit
streamlit run streamlit_app.py
```

The application will open at: **http://localhost:8501**

## Usage Workflow

### Step 1: Upload & Analyze
1. Navigate to "Upload & Analyze" page
2. Enter patient information:
   - Name, Age, Sex, Location
   - Email address (for appointment confirmation)
   - Medical history (optional)
3. Upload three medical images:
   - **Eye Image**: Clear photo of the eye
   - **Nails Image**: Photo of fingernails
   - **Tongue Image**: Photo of the tongue
4. Click "🔍 Analyze Images"
5. Wait for analysis to complete (1-2 minutes)

### Step 2: View Results
1. Navigate to "View Results" page
2. Review:
   - Comprehensive diagnosis
   - Individual analysis for each body part
   - Professional medical report
   - Personalized diet plan
   - Recommended doctors and hospitals

### Step 3: Book Appointment
1. Navigate to "Book Appointment" page
2. Select or confirm:
   - Doctor (pre-filled if recommendation available)
   - Hospital
   - Preferred date and time
   - Additional notes/concerns
3. Click "✅ Confirm Appointment Booking"
4. Receive confirmation email with appointment details

## System Architecture

```
streamlit_app.py (Main UI)
    ├── Patient Input Form
    ├── Image Upload Handler
    ├── ImageProcessor (Vision Processing)
    ├── Agents:
    │   ├── Vision Agent (Diagnosis)
    │   ├── Agent 1 (Report & Diet)
    │   └── Agent 2 (Hospital & Doctor)
    ├── Appointment Scheduler
    └── EmailNotifier (Confirmations)
```

## Key Components

### Image Processing
- Loads and preprocesses medical images
- Converts to base64 for LLM processing
- Handles various image formats

### Diagnosis Agent
- Uses vision models to analyze images
- Generates comprehensive diagnosis
- Provides individual analysis for each body part

### Report Generator (Agent 1)
- Creates professional medical reports
- Generates personalized diet plans
- Considers patient medical history

### Hospital Finder (Agent 2)
- Searches for nearby hospitals
- Finds suitable doctors by specialty
- Generates appointment recommendations

### Appointment System
- Schedules appointments with doctors
- Books with nearest suitable hospital
- Sends email confirmations

### Email Notifier
- Sends appointment confirmations
- Attaches medical reports
- Includes doctor and hospital details

## Troubleshooting

### API Key Issues
**Error**: "GROQ_API_KEY not configured"
- Solution: Check `.env` file has correct key format
- Key should start with `gsk_`

**Error**: "Email configuration error"
- Solution: Verify SMTP settings and use App Password for Gmail
- Check port 587 is not blocked by firewall

### Image Upload Issues
**Error**: "File size too large"
- Solution: Compress images to under 10MB
- Use JPEG format for smaller file sizes

**Error**: "Could not process image"
- Solution: Ensure images are clear and in supported format (JPG, PNG)
- Minimum resolution: 400x400 pixels

### Analysis Timeout
**Error**: "Analysis taking too long"
- Solution: Check internet connection
- Try again with smaller image files
- Ensure API key has sufficient quota

## Configuration Options

Edit `config.py` to customize:

```python
# Model selection
LLM_MODEL = "claude-3-sonnet-20240229"  # or other models

# Image settings
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_QUALITY = 0.9

# Search settings
MAX_HOSPITALS = 5
MAX_DOCTORS = 5

# Email settings
EMAIL_TIMEOUT = 30

# Logging
DEBUG_MODE = True
LOG_LEVEL = "INFO"
```

## Performance Tips

1. **Use GROQ for faster analysis** (free tier available)
2. **Optimize images before upload** (compress to <2MB)
3. **Run during off-peak hours** for faster API responses
4. **Keep email attachments small** (limit PDF attachments)

## Security Notes

⚠️ **Important Security Practices**:
- Never commit `.env` file to version control
- Use environment variables for all secrets
- Implement rate limiting for production
- Validate all user inputs
- Use HTTPS in production
- Encrypt sensitive patient data
- Follow HIPAA guidelines for production deployment

## Medical Disclaimer

⚠️ **Important**: This system is for diagnostic assistance only and should NOT be used as a substitute for professional medical advice. Always consult with qualified healthcare professionals for medical decisions.

## Support & Issues

For issues or feature requests:
1. Check troubleshooting section above
2. Review application logs in terminal
3. Verify API keys and configuration
4. Check internet connectivity

## Future Enhancements

- [ ] Multi-language support
- [ ] Patient history tracking
- [ ] Integration with medical records systems
- [ ] Advanced analytics dashboard
- [ ] Mobile app version
- [ ] Telemedicine integration
- [ ] Multiple report formats (PDF, XML)
- [ ] Doctor rating and review system

## License

This project is provided as-is for educational and research purposes.

---

**Version**: 2.0 (Streamlit)
**Last Updated**: April 23, 2026
**Support Email**: support@medical-ai.local
