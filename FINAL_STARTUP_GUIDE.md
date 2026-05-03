# 🚀 **COMPLETE STARTUP & USAGE GUIDE**

## **Stage 1: Start the Server**

### Option A: Windows PowerShell
```powershell
cd "AGENTIC AI"

# Activate environment (if not already active)
.\venv\Scripts\Activate.ps1

# Start server
python main_new.py

# You should see:
# ✅ Orchestrator initialized
# ✅ Vision Agent ready
# ✅ Report & Diet Agent ready
# ✅ Healthcare Discovery Agent ready
# ✅ All systems operational
# 📍 Server running at http://localhost:8000
```

### Option B: Command Prompt
```cmd
cd AGENTIC AI
venv\Scripts\activate.bat
python main_new.py
```

---

## **Stage 2: Verify Server is Running**

**Terminal 2 (New window):**

### Option A: Browser
```
Go to: http://localhost:8000/health

Should see:
{
  "status": "healthy",
  "service": "AI Medical Diagnostic System",
  "agents": {...}
}
```

### Option B: Python Script
```bash
# Terminal 2: Run test script
python test_system.py

# This will verify:
✅ Server health
✅ Demo endpoints work
✅ All agents are ready
✅ Show available endpoints
```

### Option C: cURL
```bash
curl http://localhost:8000/health
```

---

## **Stage 3: Test Demo (Quick - 1 second)**

### Using Browser (Easiest)
```
1. Go to: http://localhost:8000/docs
2. Scroll down to: POST /api/demo-analysis
3. Click green button
4. Click "Try it out"
5. Select diagnosis_type: "anemia"
6. Click blue "Execute"
7. See response ✅
```

### Using cURL
```bash
curl -X POST "http://localhost:8000/api/demo-analysis?diagnosis_type=anemia" | python -m json.tool
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/demo-analysis",
    params={"diagnosis_type": "anemia"}
)

print(response.json())
```

---

## **Stage 4: Real Analysis (With Images - 20-30 seconds)**

### Using Browser (Recommended)

**Step 1: Go to API Docs**
```
https://localhost:8000/docs
```

**Step 2: Find Endpoint**
- Look for: `POST /api/complete-analysis` (Green button)
- OR: `POST /api/analyze` (Alternative name - same endpoint)

**Step 3: Click "Try it out"**

**Step 4: Fill Form**
```
patient_name:      John Doe
patient_age:       35
patient_sex:       Male
location:          New York
medical_history:   (optional) Any relevant history
urgency:           routine
```

**Step 5: Upload Images (REQUIRED)**
```
eye_image:         [Browse & select eye.jpg]
nails_image:       [Browse & select nails.jpg]
tongue_image:      [Browse & select tongue.jpg]
```

**Step 6: Execute**
- Click blue "Execute" button
- Wait 20-30 seconds
- See complete response ✅

---

## **Stage 5: Understanding the Response**

### Response Structure
```json
{
  "status": "success",                          ← Success indicator
  "workflow_id": "WF_John_Doe_abc123",          ← Unique analysis ID
  
  "diagnosis": "Patient shows signs of...",     ← Main diagnosis
  "severity": "moderate",                       ← Severity level
  "confidence": 0.85,                           ← Confidence score
  
  "medical_report": {                           ← Agent 1 Output
    "report": "# MEDICAL REPORT\n..."
  },
  
  "diet_plan": {                                ← Agent 1 Output
    "diet_plan": "# PERSONALIZED DIET PLAN\n..."
  },
  
  "hospitals": [                                ← Agent 2 Output
    {"name": "Hospital A", "rating": "4.8"}
  ],
  
  "specialists": [                              ← Agent 2 Output
    "Hematologist", "Internal Medicine"
  ],
  
  "top_doctor_recommendation": {                ← Agent 2 Output
    "doctor": {"name": "Dr. Smith"},
    "match_score": 95
  },
  
  "appointment_slots": [                        ← Agent 2 Output
    {"date": "2026-04-10", "time": "09:00 AM"}
  ],
  
  "agents_executed": [                          ← Workflow metadata
    "vision_agent", "agent_1", "agent_2"
  ]
}
```

---

## **Stage 6: Monitor System**

### Check Agent Status
```bash
curl http://localhost:8000/api/agents/status
```

### View All Workflows
```bash
curl http://localhost:8000/api/workflows
```

### View Specific Workflow
```bash
curl http://localhost:8000/api/workflows/WF_John_Doe_abc123
```

---

## **📋 All Available Endpoints**

### Interactive (Use Browser)
```
🌐 Swagger UI:  http://localhost:8000/docs
🌐 ReDoc:       http://localhost:8000/redoc
🌐 Frontend:    http://localhost:8000/
```

### Main Endpoints
```
🏥 POST /api/complete-analysis      Complete diagnosis with all agents
🏥 POST /api/analyze                Alias (same as above)

🧪 POST /api/demo-analysis          Demo (no images needed)

🔍 POST /api/vision-analysis        Image analysis only
🔍 POST /api/report-diet            Report + diet only
🔍 POST /api/healthcare-discovery   Healthcare search only

📊 GET  /health                     Server health
📊 GET  /api/agents/status         Agent statuses
📊 GET  /api/workflows             All analyses
📊 GET  /api/workflows/{id}        Specific analysis
📊 GET  /api/info                  System info
📊 POST /api/reset                 Reset system
📊 GET  /test                      Ping test
```

---

## **🧪 Quick Test Commands**

### Test 1: Server Running (2 seconds)
```bash
curl http://localhost:8000/health
```

### Test 2: Demo Analysis (1 second)
```bash
curl -X POST "http://localhost:8000/api/demo-analysis?diagnosis_type=anemia"
```

### Test 3: Agent Status (1 second)
```bash
curl http://localhost:8000/api/agents/status
```

### Test 4: System Info (1 second)
```bash
curl http://localhost:8000/api/info
```

---

## **⚙️ Troubleshooting**

### Error: "Server not running"
```bash
# In Terminal 1:
python main_new.py

# Should show startup messages
```

### Error: "Failed to fetch"
```bash
# 1. Check server is running:
curl http://localhost:8000/health

# 2. If error, server crashed - restart:
python main_new.py

# 3. Try demo first:
curl http://localhost:8000/api/demo-analysis?diagnosis_type=anemia
```

### Error: "No images provided"
```bash
# Make sure you:
1. Upload ALL 3 images (eye, nails, tongue)
2. Use /api/complete-analysis (not demo)
3. In browser: Click "Try it out" BEFORE filling form
```

### Error: "Timeout"
```bash
# System takes 20-30 seconds
# 1. Try demo first (instant):
curl http://localhost:8000/api/demo-analysis?diagnosis_type=anemia

# 2. Check server logs for issues
# 3. Increase browser timeout (if possible)
```

### Error: "CORS issue"
```bash
# CORS is enabled by default
# If still getting error:
1. Clear browser cache
2. Try incognito mode
3. Check server is running: python main_new.py
```

---

## **📊 Workflow Diagram**

```
┌────────────────────────────────────────┐
│  Start: python main_new.py             │
└────────────────┬───────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Server Running     │
        │ http://...:8000    │
        └────────┬───────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
   [Demo]   [Test]      [Real]
  (1 sec)   (Health)   (20-30s)
      │          │          │
      └──────────┼──────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  Vision Agent      │
        │  Analyzes images   │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  Agent 1           │
        │  Report + Diet     │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  Agent 2           │
        │  Healthcare        │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  Get Results       │
        │  Diagnosis + Docs  │
        │  + Doctors +       │
        │  + Appointments    │
        └────────────────────┘
```

---

## **✨ Final Checklist**

- [ ] Terminal 1: `python main_new.py` (server running)
- [ ] Terminal 2: `curl http://localhost:8000/health` (returns healthy)
- [ ] Browser: `http://localhost:8000/docs` (Swagger UI opens)
- [ ] Test demo: `POST /api/demo-analysis?diagnosis_type=anemia` (works)
- [ ] Have 3 images ready (eye, nails, tongue)
- [ ] Fill patient info form
- [ ] Execute analysis (wait 20-30 seconds)
- [ ] View complete diagnosis + reports + doctors

---

## **🎓 Key Points**

✅ Server needs to be running: `python main_new.py`  
✅ Demo works instantly (1 second) - try this FIRST  
✅ Real analysis takes 20-30 seconds (3 agents working)  
✅ Upload ALL 3 images for real analysis  
✅ Check `/health` endpoint if having issues  
✅ Use `/docs` for interactive testing  
✅ System saves results to memory  

---

## **🚀 You're Ready!**

```
1. Start server:      python main_new.py
2. Open browser:      http://localhost:8000/docs
3. Try demo:          POST /api/demo-analysis
4. Upload images:     POST /api/complete-analysis
5. Get diagnosis:     Complete analysis in 20-30s
```

**System is fully functional and ready for use! 🏥**
