# AI Medical Diagnostic System - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Environment Setup

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
bash setup.sh
```

### 2. Configure API Keys

Edit `.env`:
```env
ANTHROPIC_API_KEY=your_claude_api_key_from_anthropic
SERPER_API_KEY=your_serper_key_optional
DEBUG_MODE=false
```

Get API keys:
- **Claude API Key**: https://console.anthropic.com
- **Serper Key (optional)**: https://serper.dev

### 3. Verify Setup

```bash
python test_setup.py
```

### 4. Start the Application

**Terminal 1 - Backend Server:**
```bash
python main.py
```

Server runs at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
# Windows
start index.html

# Mac
open index.html

# Linux
xdg-open index.html
```

Or open manually in browser: `file:///path/to/index.html`

### 5. Use the Application

1. Fill in patient information
2. Upload eye, nose, and tongue images
3. Click "Analyze Now"
4. Wait for results (15-25 seconds)
5. View diagnosis, report, diet plan, and doctors
6. Download or book appointments

---

## 📊 Example API Usage

### Using Python

```python
from image_processor import process_multipart
from vision_agent import get_diagnosis_agent
from agent_report_diet import Agent1_ReportAndDiet
from agent_hospital_doctor import Agent2_HospitalDoctor

# 1. Process images
images = process_multipart(
    eye_path='eye.jpg',
    nose_path='nose.jpg', 
    tongue_path='tongue.jpg'
)

# 2. Analyze
agent = get_diagnosis_agent()
diagnosis = agent.generate_comprehensive_diagnosis({
    "eye": images["eye"]["base64"],
    "nose": images["nose"]["base64"],
    "tongue": images["tongue"]["base64"]
})

# 3. Generate report & diet
report_agent = Agent1_ReportAndDiet()
report = report_agent.execute(
    diagnosis=diagnosis["comprehensive_diagnosis"],
    analyses=diagnosis["individual_analyses"],
    patient_info={'name': 'John Doe', 'age': 35}
)

# 4. Find doctors
doctor_agent = Agent2_HospitalDoctor()
doctors = doctor_agent.execute(
    diagnosis=diagnosis["comprehensive_diagnosis"],
    location="New York"
)
```

### Using cURL

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "eye_image=@eye.jpg" \
  -F "nose_image=@nose.jpg" \
  -F "tongue_image=@tongue.jpg" \
  -F "patient_name=John Doe" \
  -F "patient_age=35" \
  -F "location=New York"
```

### Using Python requests

```python
import requests

with open('eye.jpg', 'rb') as f1, \
     open('nose.jpg', 'rb') as f2, \
     open('tongue.jpg', 'rb') as f3:
    
    files = {
        'eye_image': f1,
        'nose_image': f2, 
        'tongue_image': f3
    }
    
    data = {
        'patient_name': 'John Doe',
        'patient_age': 35,
        'location': 'New York'
    }
    
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files=files,
        data=data
    )
    
    result = response.json()
    print(result['diagnosis'])
    print(result['report'])
    print(result['diet_plan'])
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

```bash
pip install anthropic
```

### "ANTHROPIC_API_KEY not found"

1. Create `.env` file: `cp .env.example .env`
2. Add your API key: `ANTHROPIC_API_KEY=sk-...`

### "Image not found" error

Ensure images are in supported formats: JPG, PNG, WebP, BMP

### Slow response

Claude API has rate limiting. Wait between requests.

### "Port 8000 already in use"

Use different port:
```bash
# Edit main.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 🎯 Core Features

| Feature | Status | Notes |
|---------|--------|-------|
| Eye analysis | ✅ | Detects anemia, jaundice, diabetes signs |
| Nose analysis | ✅ | Identifies infections, inflammation |
| Tongue analysis | ✅ | Vitamin deficiency detection |
| Medical reports | ✅ | Professional format, downloadable |
| Diet plans | ✅ | 30-day personalized recommendations |
| Doctor finder | ✅ | Location-based search with ranking |
| Hospital search | ✅ | Nearby healthcare providers |
| Appointments | ✅ | Scheduling system integrated |

---

## 📚 Documentation

- Full docs: [README.md](README.md)
- API docs: http://localhost:8000/docs (when running)
- Config guide: [config.py](config.py)

---

## 🆘 Support

If you encounter issues:

1. Run: `python test_setup.py`
2. Check logs in `logs/`
3. Verify `.env` configuration
4. Ensure all images are valid

---

## 🚀 Next Steps

1. **Customize**: Edit analysis prompts in `vision_agent.py`
2. **Deploy**: Use Docker or cloud platform
3. **Integrate**: Add to your healthcare app
4. **Scale**: Set up database for patient history

Happy diagnosing! 🏥
