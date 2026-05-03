# AI Medical Diagnostic System - Architecture & Design

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (User Interface)              │
│                         index.html                          │
│  - Patient information form                                 │
│  - Image upload (eye, nose, tongue)                        │
│  - Real-time results display                               │
│  - Report & diet plan download                             │
│  - Appointment booking UI                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (main.py)                     │
│                                                             │
│  Core Endpoints:                                           │
│  ├── POST /api/analyze         (Main analysis)            │
│  ├── POST /api/single-image    (Single image)             │
│  ├── GET  /api/reports         (List reports)             │
│  ├── GET  /api/reports/{id}    (Get report)               │
│  ├── POST /api/book-appointment (Book appointment)        │
│  ├── GET  /health              (Health check)             │
│  └── GET  /api/stats           (Statistics)               │
└────────────────┬────────────────────────┬──────────────────┘
                 │                         │
        ┌────────▼────────┐       ┌───────▼──────────┐
        │  Image Pipeline │       │  Agent Orchestra │
        └────────┬────────┘       └───────┬──────────┘
                 │                         │
    ┌────────────┼─────────────┐   ┌──────┼──────────────┐
    │            │             │   │      │              │
    ▼            ▼             ▼   ▼      ▼              ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  ┌─────────┐
│  Image  │ │ Preproc- │ │  Base64  │ │Vision  │  │Agent 1  │
│ Loader  │ │  essing  │ │ Encoding │ │Agent   │  │Report   │
│         │ │ (CLAHE)  │ │          │ │(Claude)│  │& Diet   │
├─────────┤ ├──────────┤ ├──────────┤ └───┬────┘  ├─────────┤
│ • Load  │ │• Resize  │ │• JPEG    │     │       │• Medical│
│• Validate│ │• Normalize│• To API  │  Eye│       │ Report  │
│• Format │ │• Extract │• Config   │  Nose│      │• Diet   │
│  Check  │ │  ROI     │• Optimize │ Tongue      │  Plan   │
└─────────┘ └──────────┘ └──────────┘     │       └────┬────┘
                                           │            │
                                      ┌────▼────────┐   │
                                      │Comprehensive│   │
                                      │ Diagnosis   │   │
                                      └────┬────────┘   │
                                           │            │
                    ┌──────────────────────┼────────────┘
                    │                      │
                    ▼                      ▼
            ┌──────────────────┐   ┌────────────┐
            │   Agent 2        │   │ File System│
            │ Hospital Finder  │   │            │
            ├──────────────────┤   ├────────────┤
            │• Web Search      │   │• Reports/  │
            │• Doctor Ranking  │   │• Diet plans│
            │• Appointments    │   │• Logs/     │
            └──────────────────┘   └────────────┘
```

## 🔄 Data Flow Diagram

```
User Upload
    │
    ▼
┌──────────────────────┐
│ Image File Upload    │
│ (eye, nose, tongue)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Image Processing     │
│ • Load & Validate    │
│ • Preprocess (CLAHE) │
│ • Extract ROI        │
│ • Convert to Base64  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│ Vision Analysis (Claude)     │
│ Eye    → Anemia, Jaundice    │
│ Nose   → Infection, Polyps   │
│ Tongue → B12, Iron Deficiency│
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────┐
│ Comprehensive Diagnosis  │
│ (Synthesis of all data)  │
└──────────┬───────────────┘
           │
           ├──────────────┬──────────────┐
           │              │              │
           ▼              ▼              ▼
      ┌─────────┐   ┌──────────┐   ┌──────────┐
      │Agent 1  │   │Agent 2   │   │Database  │
      │─────────│   │──────────│   │──────────│
      │ Medical │   │Hospitals/│   │ History  │
      │ Report  │   │Doctors   │   │ Storage  │
      │ Diet    │   │Appt      │   │Patient   │
      │ Plan    │   │Scheduling│   │Analysis  │
      └────┬────┘   └────┬─────┘   └────┬─────┘
           │             │              │
           └─────────┬───┴──────────────┘
                     │
                     ▼
           ┌──────────────────────┐
           │ Results Compiled     │
           │ • Diagnosis          │
           │ • Report             │
           │ • Diet Plan          │
           │ • Doctors            │
           │ • Appointments       │
           └──────────┬───────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │ Return to Frontend   │
           │ (JSON Response)      │
           └──────────┬───────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │ Display Results      │
           │ • Tabs for each view │
           │ • Download options   │
           │ • Booking interface  │
           └──────────────────────┘
```

## 🔧 Component Details

### 1. Image Processor (`image_processor.py`)

**Responsibilities:**
- Load images from file or bytes
- Resize to standard dimensions (512x512)
- Apply CLAHE for contrast enhancement
- Extract ROI specific to body part
- Convert to base64 for API transmission
- Batch processing support

**Key Methods:**
```python
load_image()           # Load from file
load_from_bytes()      # Load from bytes
preprocess()           # Size, normalize, enhance
extract_roi()          # Get specific region
to_base64()            # Encode for API
```

### 2. Vision Agent (`vision_agent.py`)

**Responsibilities:**
- Communicate with Claude Vision API
- Analyze eye images
- Analyze nose images
- Analyze tongue images
- Synthesize all analyses into comprehensive diagnosis

**Key Methods:**
```python
analyze_medical_image()              # Single image analysis
generate_comprehensive_diagnosis()   # All 3 images
_get_system_prompt()                 # Specialist prompts
_get_analysis_prompt()               # Detailed questions
```

### 3. Agent 1: Report & Diet (`agent_report_diet.py`)

**Responsibilities:**
- Generate professional medical reports
- Create personalized diet plans
- Save documents to files
- Severity-based recommendations

**Key Classes:**
```python
ReportGenerator        # Medical report creation
DietPlanGenerator      # Personalized diet plans
Agent1_ReportAndDiet   # Coordination
```

**Report Contents:**
- Clinical summary
- Detailed findings
- Assessment (status, severity, confidence)
- Key findings
- Recommendations
- Follow-up requirements

**Diet Plan Contents:**
- Executive summary
- Nutritional goals
- Foods to prioritize (by category)
- Foods to avoid
- Weekly meal suggestions
- Recipes with instruction
- Supplements (if needed)
- Progress tracking

### 4. Agent 2: Hospital Finder (`agent_hospital_doctor.py`)

**Responsibilities:**
- Search for nearby hospitals
- Find specialty doctors
- Rank doctors by diagnosis match
- Suggest appointment times
- Create appointment records
- Send reminders

**Key Classes:**
```python
WebSearchEngine           # Serper API integration
DoctorRecommender         # LLM-based ranking
AppointmentScheduler      # Appointment management
Agent2_HospitalDoctor     # Coordination
```

### 5. FastAPI Backend (`main.py`)

**Responsibilities:**
- API endpoint management
- Request validation
- File upload handling
- Agent orchestration
- Response formatting
- Error handling
- Logging

**Endpoint Groups:**
- Analysis endpoints
- Report management
- Appointment system
- Health checks

### 6. Frontend (`index.html`)

**Responsibilities:**
- User interface
- Form handling
- Real-time feedback
- Results display
- File download
- Appointment booking

**UI Sections:**
- Patient information form
- Image upload area
- Results display (tabbed)
- Download buttons
- Appointment interface

## 🔑 Key Data Structures

### Request Model
```python
{
    "patient_info": {
        "name": str,
        "age": int,
        "sex": str,
        "location": str,
        "medical_history": str,
        "allergies": list,
        "medications": list
    },
    "location": str,
    "urgency": str
}
```

### Response Model
```python
{
    "status": "success" | "error",
    "diagnosis": str,
    "analyses": {
        "eye": {"status": str, "analysis": str},
        "nose": {"status": str, "analysis": str},
        "tongue": {"status": str, "analysis": str}
    },
    "report": str,
    "diet_plan": str,
    "hospitals": [
        {"name": str, "address": str, "rating": str}
    ],
    "doctors": [
        {"name": str, "specialty": str, "score": float}
    ],
    "appointments": [
        {"date": str, "time": str, "doctor": str}
    ]
}
```

## 🔌 External Integrations

### Anthropic Claude API
- **Model**: claude-3-5-sonnet-20241022
- **Capabilities**: Vision + Text (multimodal)
- **Usage**: 
  - Analyze medical images
  - Generate detailed reports
  - Rank doctors
  - Create diet plans

### Serper API
- **Service**: Web search
- **Usage**:
  - Hospital discovery
  - Doctor search
  - Appointment availability
- **Alternative**: Can use Google Custom Search or Bing

## 📊 Processing Pipeline

```
1. User uploads 3 images + patient info
         ↓
2. Validate image format and size
         ↓
3. Load images and preprocess
         ↓
4. Extract ROI for each body part
         ↓
5. Convert to base64 encoding
         ↓
6. Send to Claude Vision API
         ↓
7. Receive individual analyses
         ↓
8. Generate comprehensive diagnosis
         ↓
9. Agent 1: Create medical report
         ↓
10. Agent 1: Generate diet plan
         ↓
11. Agent 2: Search for hospitals
         ↓
12. Agent 2: Find doctors
         ↓
13. Agent 2: Rank doctors
         ↓
14. Agent 2: Suggest appointments
         ↓
15. Compile all results
         ↓
16. Return JSON response
         ↓
17. Display in frontend
```

## ⚙️ Configuration Management

**Hierarchy:**
```
System Environment
    ↓
.env file
    ↓
config.py
    ↓
Individual Components
```

**Key Config Items:**
- API Keys (Anthropic, Serper)
- Model Selection
- Image Processing Parameters
- Database URL
- Report Templates
- Specialty Mappings

## 🔒 Security Architecture

```
┌─────────────────────────────────────────┐
│      Public Internet                    │
└────┬──────────────────────────────────┬─┘
     │                                  │
     ▼                                  ▼
┌──────────┐                      ┌──────────┐
│ User     │                      │ APIs     │
│Frontend  │◄────HTTP/REST───────►│ (Claude) │
│(Browser) │                      │(Serper)  │
└──────────┘                      └──────────┘
     │
     │ CORS
     │ Validation
     │ Rate Limiting
     ▼
┌─────────────────────────┐
│  Backend Server         │
│  (FastAPI)              │
│                         │
│ • Input Validation      │
│ • Error Handling        │
│ • Logging               │
│ • Rate Limiting         │
│ • Session Management    │
└──────┬──────────────────┘
       │
       ├────────┬──────────┬──────────┐
       │        │          │          │
       ▼        ▼          ▼          ▼
    Images  Reports  Database   Cache
  (Deleted)(Files)   (Optional) (Temp)
```

**Security Measures:**
- API keys in .env (never committed)
- Input validation on all endpoints
- CORS configured
- No sensitive data in logs
- Images deleted after processing
- Rate limiting ready
- Authentication hooks prepared

## 📈 Scalability Considerations

### Current State (Single Instance)
- Handles ~10 concurrent requests
- ~15-25 seconds per analysis
- Memory: ~200-500MB

### Production Scaling Options
1. **Horizontal Scaling**
   - Load balancer (Nginx, HAProxy)
   - Multiple backend instances
   - Message queue (Celery, RabbitMQ)
   - Task workers

2. **Caching**
   - Redis for API responses
   - Image cache
   - Doctor/hospital cache

3. **Database**
   - PostgreSQL for production
   - Connection pooling
   - Backup strategy

4. **CDN**
   - Frontend assets
   - Static reports
   - Report downloads

## 🎯 Design Principles

1. **Modularity**: Each component is independent
2. **Extensibility**: Easy to add new agents
3. **Maintainability**: Clean code, comprehensive logging
4. **Performance**: Async operations, caching
5. **Security**: Input validation, API key management
6. **Usability**: Intuitive UI, clear results

## 🚀 Future Enhancements

```
Phase 2:
├── Authentication & Authorization
├── Patient history/profiles
├── Real-time collaboration
├── Advanced analytics dashboard
└── Integration with EHR systems

Phase 3:
├── Mobile app (React Native)
├── Telemedicine scheduling
├── ML model for prediction
├── Multi-language support
└── Insurance integration
```

---

**Architecture Version**: 1.0.0  
**Last Updated**: April 2026  
**Status**: Production Ready ✅
