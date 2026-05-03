"""
Simple server runner with better error handling
"""
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("Starting AI Medical Diagnostic System")
print("="*60 + "\n")

try:
    print("✓ Importing dependencies...")
    import uvicorn
    from config import ANTHROPIC_API_KEY, GROQ_API_KEY, DEBUG_MODE, USE_GROQ
    print("  - Imports successful")
    
    # Check API key
    print("\n✓ Checking configuration...")
    from config import GROQ_API_KEY, USE_GROQ
    
    if USE_GROQ:
        if not GROQ_API_KEY or GROQ_API_KEY == "paste_your_groq_api_key_here":
            print("  ❌ ERROR: GROQ_API_KEY not configured!")
            print("     Please edit .env file and add your Groq API key:")
            print("     GROQ_API_KEY=gsk_your_actual_key_here")
            print("\n     Get free key from: https://console.groq.com/keys")
            sys.exit(1)
        print("  ✓ Groq API Key configured ✓")
    else:
        if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_claude_api_key_here":
            print("  ❌ ERROR: ANTHROPIC_API_KEY not configured!")
            print("     Please edit .env file and add your Claude API key:")
            print("     ANTHROPIC_API_KEY=sk-ant-your_actual_key_here")
            sys.exit(1)
        print("  ✓ Anthropic Claude API Key configured")
    print(f"  ✓ Debug mode: {DEBUG_MODE}")
    
    print("\n✓ Initializing FastAPI app...")
    from main import app
    print("  ✓ App initialized")
    
    print("\n✓ Starting Uvicorn server...\n")
    print("="*60)
    print("🚀 Server is running!")
    print("="*60)
    print("\n📍 Local URL:  http://127.0.0.1:8000")
    print("📍 Open UI:    Open index.html in your browser")
    print("📍 API Docs:   http://127.0.0.1:8000/docs")
    print("📍 Stop:       Press Ctrl+C")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info" if DEBUG_MODE else "error"
    )

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nMissing module. Run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
