# 🚀 QUICK START - COMPLETE AGENTIC SYSTEM

## 📋 Setup (5 minutes)

### 1. **Install Dependencies**
```bash
cd "AGENTIC AI"

# Create virtual environment
python -m venv venv

# Activate 
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Add Groq (free LLM)
pip install groq
```

### 2. **Configure Environment**
```bash
# Copy template
cp .env.example .env

# Edit .env:
GROQ_API_KEY=gsk_your_key_here
USE_GROQ=true
```

### 3. **Install & Start Ollama (Optional - for Llama 3)**
```bash
# Download from https://ollama.ai

# Pull Llama 3
ollama pull llama3

# Start Ollama service
ollama serve

# In another terminal, verify:
curl http://localhost:11434/api/tags
```

---

## 🏃 Run the System

### **Start Backend**
```bash
python main_new.py

# You should see:
# ✅ Orchestrator initialized
# ✅ Vision Agent ready
# ✅ Report & Diet Agent ready
# ✅ Healthcare Discovery Agent ready
# ✅ Server running at http://localhost:8000
```

### **Access the System**
```
📍 Frontend:   http://localhost:8000/
📍 API Docs:   http://localhost:8000/docs
📍 ReDoc:      http://localhost:8000/redoc
```

---

## 🧪 Test Complete Workflow

### **Using API Docs (Easiest)**
1. Go to http://localhost:8000/docs
2. Click on `/api/complete-analysis`
3. Click "Try it out"
4. Fill in fields:
   - `patient_name`: John Doe
   - `patient_age`: 35
   - `patient_sex`: Male
   - `location`: New York
   - Upload 3 images (eye, nails, tongue)
5. Click "Execute"
6. See results!

### **Using cURL**
```bash
curl -X POST "http://localhost:8000/api/complete-analysis" \
  -F "patient_name=John Doe" \
  -F "patient_age=35" \
  -F "patient_sex=Male" \
  -F "location=New York" \
  -F "eye_image=@path/to/eye.jpg" \
  -F "nails_image=@path/to/nails.jpg" \
  -F "tongue_image=@path/to/tongue.jpg"
```

### **Using Python**
```python
import requests

files = {
    'eye_image': open('eye.jpg', 'rb'),
    'nails_image': open('nails.jpg', 'rb'),
    'tongue_image': open('tongue.jpg', 'rb'),
}

data = {
    'patient_name': 'John Doe',
    'patient_age': 35,
    'patient_sex': 'Male',
    'location': 'New York'
}

response = requests.post(
    'http://localhost:8000/api/complete-analysis',
    files=files,
    data=data
)

print(response.json())
```

---

## 🤖 Complete Workflow (Behind the Scenes)

```
1. IMAGE UPLOAD
   ↓
2. VISION AGENT
   • Analyzes eye, nails, tongue
   • Generates diagnosis
   • Reports confidence scores
   ↓
3. AGENT 1: REPORT & DIET
   • Creates medical report
   • Generates diet plan
   • Saves documents
   ↓
4. AGENT 2: HEALTHCARE
   • Searches hospitals
   • Finds specialists
   • Suggests appointments
   ↓
5. RESULTS CONSOLIDATED
   ✅ Complete analysis ready
```

---

## 📊 Response Example

```json
{
  "status": "success",
  "workflow_id": "WF_John_Doe_abc123",
  "patient": {
    "name": "John Doe",
    "age": 35,
    "sex": "Male",
    "location": "New York"
  },
  "diagnosis": "Patient shows signs of iron deficiency based on pale conjunctiva and tongue analysis...",
  "severity": "moderate",
  "confidence": 0.85,
  
  "medical_report": {
    "status": "success",
    "report": "# MEDICAL REPORT\n**Report Date:** 2026-04-09\n... detailed clinical findings ..."
  },
  
  "diet_plan": {
    "status": "success",
    "diet_plan": "# PERSONALIZED DIET PLAN\n**Duration:** 30 days\n... meal suggestions ..."
  },
  
  "hospitals": [
    {
      "name": "General Hospital NYC",
      "address": "123 Main St",
      "link": "https://..."
    }
  ],
  
  "specialists": ["Hematologist", "Internal Medicine"],
  
  "top_doctor_recommendation": {
    "doctor": {
      "name": "Dr. Smith",
      "specialty": "Hematologist",
      "match_score": 95
    }
  },
  
  "appointment_slots": [
    {
      "date": "2026-04-10",
      "time": "09:00 AM",
      "doctor": "Dr. Smith"
    }
  ],
  
  "agents_executed": ["vision_agent", "agent_1", "agent_2"],
  "timestamp": "2026-04-09T10:30:45.123Z"
}
```

---

## 🎯 Individual Agent Endpoints

### **Vision Analysis Only**
```bash
POST /api/vision-analysis
- Upload 3 images
- Get diagnosis only
```

### **Report & Diet Only**
```bash
POST /api/report-diet?diagnosis=...&severity=moderate
- Provide diagnosis
- Get report + diet plan
```

### **Healthcare Discovery Only**
```bash
POST /api/healthcare-discovery?diagnosis=...&location=...
- Provide diagnosis & location
- Get hospitals + doctors
```

---

## 📈 Monitor System

### **Check Agent Status**
```bash
curl http://localhost:8000/api/agents/status
```

### **View All Workflows**
```bash
curl http://localhost:8000/api/workflows
```

### **View Specific Workflow**
```bash
curl http://localhost:8000/api/workflows/WF_patient_xyz123
```

### **System Health**
```bash
curl http://localhost:8000/health
```

---

## 🔧 Troubleshooting

### **"ModuleNotFoundError: No module named..."**
```bash
pip install -r requirements.txt -U
```

### **"Groq API Key not found"**
```bash
# Check .env file has:
GROQ_API_KEY=gsk_...
USE_GROQ=true
```

### **"Ollama not found"**
```bash
# If using Llama 3 locally:
# 1. Download from https://ollama.ai
# 2. Run: ollama serve
# 3. In new terminal: ollama pull llama3
```

### **"Image files not found"**
```bash
#  Make sure image paths are correct:
# - Must be absolute paths or relative from current directory
# - Supported formats: jpg, jpeg, png, bmp, webp
# - Max size: 20MB each
```

---

## 🌟 What's Happening Under the Hood

### **Vision Agent**
- Uses Claude Vision or Groq Mixtral
- Analyzes 3 medical images simultaneously
- Detects 15+ medical conditions per body part
- Generates structured diagnostic findings

### **Agent 1: Report & Diet**
- Processes diagnosis from Vision Agent
- Generates professional medical report (clinical, detailed, assessment, recommendations)
- Creates personalized 30-day diet plan
- Saves documents to `reports/` folder

### **Agent 2: Healthcare Discovery**
- Searches for hospitals using Serper API or local database
- Finds specialists matching diagnosis
- Ranks doctors by relevance using LLM
- Suggests appointment slots

---

## 💡 Tips

1. **Use better images** → More accurate diagnosis
2. **Provide medical history** → Better recommendations
3. **Check confidence scores** → Indicates reliability
4. **Download generated reports** → Patient records

---

## 📁 Key Files

```
main_new.py              ← Complete agentic backend
agent_orchestrator.py    ← Multi-agent conductor
vision_agent.py          ← Image analysis
agent_report_diet.py     ← Documents
agent_hospital_doctor.py ← Healthcare search
config.py                ← Environment variables
.env                     ← API keys (create from .env.example)
```

---

## 🎓 Next Steps

1. ✅ **Run the system** - `python main_new.py`
2. ✅ **Test with sample images** - Use `/docs` interface
3. ✅ **Monitor workflows** - Check `/api/workflows`
4. ✅ **Generate reports** - Download PDFs from results
5. ✅ **Find doctors** - Get recommendations

---

## 🚀 Production Deployment

```bash
# Use Gunicorn for production
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:8000 main_new:app

# Or with PM2
npm install -g pm2
pm2 start "python main_new.py" --name "medical-ai"
```

---

## 🤝 Support

For issues or questions:
1. Check logs in console output
2. Visit API docs at `/docs`
3. Review error messages in response
4. Check file permissions in `uploads/`, `reports/`, `logs/`

**You're all set! Start diagnosing! 🏥**
