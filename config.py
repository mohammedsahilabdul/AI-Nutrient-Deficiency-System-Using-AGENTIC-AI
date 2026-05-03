"""
Configuration Management
Handles all API keys, model settings, and environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ========================
# API KEYS & CREDENTIALS
# ========================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Free alternative
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")  # For web search
GMAIL_CREDENTIALS = os.getenv("GMAIL_CREDENTIALS", "")

# ========================
# EMAIL CONFIGURATION
# ========================
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
# Support both naming conventions
SENDER_EMAIL = os.getenv("SENDER_EMAIL") or os.getenv("GMAIL_SENDER", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") or os.getenv("GMAIL_PASSWORD", "")
EMAIL_TIMEOUT = 30

# ========================
# MODEL CONFIGURATION
# ========================
# Using Groq (free, fast API)
USE_GROQ = os.getenv("USE_GROQ", "true").lower() == "true"
LLM_MODEL = "mixtral-8x7b-32768" if USE_GROQ else "claude-3-5-sonnet-20241022"
VISION_MODEL = "mixtral-8x7b-32768" if USE_GROQ else "claude-3-5-sonnet-20241022"

# Alternative: Use vLLM locally
VLLM_SERVER_URL = os.getenv("VLLM_SERVER_URL", "http://localhost:8000")
USE_VLLM_LOCAL = os.getenv("USE_VLLM_LOCAL", "false").lower() == "true"

# Models if using vLLM locally (e.g., Llama 2, Mistral, etc.)
VLLM_MODEL = os.getenv("VLLM_MODEL", "meta-llama/Llama-2-7b-hf")

# ========================
# IMAGE PROCESSING
# ========================
IMAGE_SIZE = (512, 512)
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "bmp", "webp"]
MAX_IMAGE_SIZE_MB = 20
IMAGE_QUALITY = 95

# ========================
# DATABASE
# ========================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_db.db")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ========================
# AGENT SETTINGS
# ========================
SEARCH_ENGINE = "serper"  # or "google" or "bing"
MAX_SEARCH_RESULTS = 5
DOCTOR_SPECIALTY_WEIGHT = {
    "Dermatology": 10,
    "General Practitioner": 7,
    "Internal Medicine": 8
}

# ========================
# REPORT GENERATION
# ========================
REPORT_TEMPLATE_PATH = "templates/medical_report_template.html"
DIET_PLAN_CATEGORIES = [
    "Vitamins & Minerals",
    "Proteins",
    "Carbohydrates",
    "Healthy Fats",
    "Hydration",
    "Foods to Avoid"
]

# ========================
# CACHE & MEMORY
# ========================
CACHE_DIR = "cache"
MEMORY_DIR = "memory"
MAX_CACHE_SIZE_MB = 500

# Create required directories
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
