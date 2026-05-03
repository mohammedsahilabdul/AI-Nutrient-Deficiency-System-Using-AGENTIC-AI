# AI Medical Diagnostic System

A sophisticated medical diagnosis platform using multimodal AI image analysis (eyes, nose, tongue) combined with agentic AI for intelligent recommendations.

## 🎯 Overview

This system performs comprehensive medical analysis through:

1. **Multi-Modal Image Analysis** - Analyzes eye, nose, and tongue images using Claude Vision
2. **Intelligent Diagnosis** - Provides clinical diagnosis and findings
3. **Agent 1: Report & Diet Generation** - Generates detailed medical reports and personalized diet plans
4. **Agent 2: Healthcare Provider Discovery** - Finds suitable hospitals and doctors

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Web User Interface              │
│          (HTML/CSS/JS)                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    FastAPI Backend Server               │
│    (main.py)                            │
└─────┬──────────┬──────────┬──────────┬──┘
      │          │          │          │
      ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌────────┐ ┌─────────────┐
│  Image   │ │ Vision   │ │Agent 1 │ │  Agent 2    │
│Processor │ │  Agent   │ │Report& │ │Hospital &   │
│          │ │ (Claude) │ │Diet    │ │Doctor Finder│
└──────────┘ └──────────┘ └────────┘ └─────────────┘
```

## 📋 Components

### 1. **Image Processor** (`image_processor.py`)
- Loads and preprocesses medical images
- Extracts regions of interest (ROI)
- Applies contrast enhancement (CLAHE)
- Converts to base64 for LLM transmission

### 2. **Vision Agent** (`vision_agent.py`)
- Claude 3.5 Sonnet vision model integration
- Specialized analysis prompts for each body part
- Individual and comprehensive analysis

### 3. **Agent 1 - Report & Diet Generator** (`agent_report_diet.py`)
- Generates professional medical reports
- Creates personalized diet plans
- Saves documents to files

### 4. **Agent 2 - Hospital/Doctor Finder** (`agent_hospital_doctor.py`)
- Web search integration (Serper API)
- Doctor ranking using LLM
- Appointment scheduling system
- Hospital discovery

### 5. **FastAPI Backend** (`main.py`)
- RESTful API endpoints
- Multi-image upload handling
- Orchestrates all agents
- Returns comprehensive analysis results

### 6. **Web Frontend** (`index.html`)
- Interactive UI for image upload
- Real-time results display
- Report and diet plan download
- Appointment booking interface

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- pip or conda
- Anthropic API Key (for Claude access)
- Serper API Key (optional, for doctor/hospital search)

### 1. Clone & Navigate
```bash
cd "AGENTIC AI"
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env with your API keys
```

Edit `.env`:
```env
ANTHROPIC_API_KEY=your_claude_api_key_here
SERPER_API_KEY=your_serper_api_key_here
DEBUG_MODE=false
```

### 5. Run the Application

**Start the backend server:**
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

**Access the frontend:**
Open `index.html` in your browser or serve it:
```bash
# Simple HTTP server
python -m http.server 8080

# Then open: http://localhost:8080
```

## 📚 API Endpoints

### POST `/api/analyze`
Upload three medical images and analyze

**Parameters:**
- `eye_image` - Eye image file (required)
- `nose_image` - Nose image file (required)
- `tongue_image` - Tongue image file (required)
- `patient_name` - Patient name (optional)
- `patient_age` - Patient age (optional)
- `patient_sex` - Patient sex (optional)
- `location` - Patient location (for doctor search)
- `medical_history` - Medical history (optional)

**Response:**
```json
{
  "status": "success",
  "diagnosis": "Clinical diagnosis summary",
  "analyses": {
    "eye": {"status": "processed", "analysis": "..."},
    "nose": {"status": "processed", "analysis": "..."},
    "tongue": {"status": "processed", "analysis": "..."}
  },
  "report": "Medical report text",
  "diet_plan": "Personalized diet plan",
  "hospitals": [{...}],
  "doctors": [{...}],
  "appointments": [{...}]
}
```

### GET `/health`
Health check

### GET `/api/reports`
List all generated reports

### GET `/api/reports/{report_name}`
Download specific report

### POST `/api/book-appointment`
Book appointment with doctor

## 🎨 Features

### Image Analysis
- ✅ Eye analysis for systemic diseases (anemia, diabetes, hypertension)
- ✅ Nose analysis for infections and inflammation
- ✅ Tongue analysis for nutritional deficiencies and systemic conditions
- ✅ ROI extraction specific to each body part
- ✅ Contrast enhancement for better visibility

### Report Generation (Agent 1)
- ✅ Professional medical reports
- ✅ Personalized diet plans (30-day)
- ✅ Severity assessment
- ✅ Recommendation-based actions
- ✅ Markdown and file export

### Healthcare Discovery (Agent 2)
- ✅ Hospital search by location and specialty
- ✅ Doctor ranking by diagnosis match
- ✅ Appointment slot suggestions
- ✅ LLM-powered doctor recommendations
- ✅ Web search integration

### User Interface
- ✅ Responsive design
- ✅ Real-time loading feedback
- ✅ Tab-based result navigation
- ✅ Download functionality
- ✅ Appointment booking

## 🔧 Configuration

### Model Selection
Edit `config.py` to switch models:

```python
# Use Claude (default)
LLM_MODEL = "claude-3-5-sonnet-20241022"

# Or use local vLLM
USE_VLLM_LOCAL = True
VLLM_SERVER_URL = "http://localhost:8000"
VLLM_MODEL = "meta-llama/Llama-2-7b-hf"
```

### Customize Body Part Analysis
Modify system prompts in `vision_agent.py`:
```python
def _get_system_prompt(self, body_part: str) -> str:
    prompts = {
        "eye": "Custom eye analysis prompt...",
        "nose": "Custom nose analysis prompt...",
        "tongue": "Custom tongue analysis prompt..."
    }
```

## 📊 Example Usage

### Python Script
```python
from vision_agent import get_diagnosis_agent
from agent_report_diet import Agent1_ReportAndDiet
from agent_hospital_doctor import Agent2_HospitalDoctor

# 1. Analyze images
agent = get_diagnosis_agent()
result = agent.generate_comprehensive_diagnosis({
    "eye": base64_eye_image,
    "nose": base64_nose_image,
    "tongue": base64_tongue_image
})

# 2. Generate report & diet
report_agent = Agent1_ReportAndDiet()
report = report_agent.execute(
    diagnosis=result["comprehensive_diagnosis"],
    analyses=result["individual_analyses"]
)

# 3. Find doctors
doctor_agent = Agent2_HospitalDoctor()
doctors = doctor_agent.execute(
    diagnosis=result["comprehensive_diagnosis"],
    location="New York"
)
```

### cURL
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "eye_image=@eye.jpg" \
  -F "nose_image=@nose.jpg" \
  -F "tongue_image=@tongue.jpg" \
  -F "patient_name=John Doe" \
  -F "patient_age=35" \
  -F "location=New York"
```

## 📈 Performance

- Image processing: ~2-3 seconds
- Vision analysis: ~5-10 seconds (Claude API)
- Report generation: ~3-5 seconds
- Doctor search: ~2-4 seconds
- **Total:** ~15-25 seconds for complete analysis

## 🔐 Security & Privacy

- ✅ No images stored permanently (processed and deleted)
- ✅ API key stored in `.env` (not in version control)
- ✅ HTTPS ready (configure in production)
- ✅ CORS restricted to known domains
- ✅ Input validation on all endpoints

## 🚀 Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "main.py"]
```

Deploy:
```bash
docker build -t medical-ai .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=xxx medical-ai
```

### Environment Variables for Production
```env
ANTHROPIC_API_KEY=your_production_key
SERPER_API_KEY=your_production_key
DEBUG_MODE=false
DATABASE_URL=postgresql://user:pass@db:5432/medical_db
```

## 🛠️ Troubleshooting

### Issue: "API Key Not Found"
**Solution:** Make sure `.env` file exists and has `ANTHROPIC_API_KEY`

### Issue: "Image not recognized"
**Solution:** Ensure images are in supported formats (JPG, PNG, WebP)

### Issue: "No doctors found"
**Solution:** Check Serper API key and internet connection

### Issue: Slow analysis
**Solution:** Claude API calls are rate-limited. Wait between requests.

## 📝 Logging

View logs in `logs/conversations.json` for all analysis history

## 🤝 Contributing

Fork → Branch → Commit → Push → Pull Request

## 📄 License

MIT License - See LICENSE file

## 👨‍💼 Support

For issues, questions, or feedback:
- Create an issue on GitHub
- Contact: support@medicalai.dev

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Real-time camera capture
- [ ] Patient history tracking
- [ ] Insurance integration
- [ ] Telemedicine scheduling
- [ ] Export to FHIR format
- [ ] Machine learning model training
- [ ] Mobile app (React Native)

---

**Version:** 1.0.0  
**Last Updated:** April 2026  
**Status:** Production Ready ✅
