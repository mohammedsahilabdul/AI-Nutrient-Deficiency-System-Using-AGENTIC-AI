#!/usr/bin/env python3
"""
STREAMLIT SETUP VERIFICATION SCRIPT
Run this to verify your system is ready
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if file exists"""
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {description}: {path}")
    return exists

def check_env_file():
    """Check .env file configuration"""
    env_path = ".env"
    if not Path(env_path).exists():
        print("  ❌ .env file NOT FOUND")
        print("     Action: Copy .env.template to .env and add your API keys")
        return False
    
    print("  ✅ .env file found")
    
    # Check required keys
    with open(env_path) as f:
        content = f.read()
    
    required_keys = {
        "USE_GROQ": "LLM Configuration",
        "GROQ_API_KEY": "GROQ API Key (for LLM)",
        "SMTP_SERVER": "Email Configuration",
        "SENDER_EMAIL": "Email Address",
        "SENDER_PASSWORD": "Email App Password"
    }
    
    all_found = True
    for key, description in required_keys.items():
        if key in content and not content.strip().startswith(f"# {key}"):
            print(f"    ✅ {description}")
        else:
            print(f"    ❌ {description} - NOT configured")
            all_found = False
    
    return all_found

def main():
    print("\n" + "="*60)
    print("🏥 AI MEDICAL DIAGNOSTIC SYSTEM - SETUP VERIFICATION")
    print("="*60 + "\n")
    
    print("📋 CHECKING FILES...\n")
    
    files_ok = True
    files_ok &= check_file("streamlit_app.py", "Main Application")
    files_ok &= check_file(".env.template", "Configuration Template")
    files_ok &= check_file("requirements.txt", "Dependencies List")
    files_ok &= check_file("config.py", "Configuration Module")
    files_ok &= check_file("run_streamlit.bat", "Windows Launcher")
    files_ok &= check_file("run_streamlit.sh", "Linux/Mac Launcher")
    
    print("\n📧 CHECKING CONFIGURATION...\n")
    config_ok = check_env_file()
    
    print("\n📦 CHECKING DEPENDENCIES...\n")
    try:
        import streamlit
        print(f"  ✅ Streamlit installed (v{streamlit.__version__})")
        deps_ok = True
    except ImportError:
        print("  ❌ Streamlit NOT installed")
        print("     Action: Run: pip install streamlit==1.28.1")
        deps_ok = False
    
    print("\n" + "="*60)
    print("🔍 VERIFICATION RESULTS")
    print("="*60 + "\n")
    
    if files_ok:
        print("✅ All required files are present\n")
    else:
        print("❌ Some files are missing\n")
    
    if config_ok:
        print("✅ Configuration is complete\n")
    else:
        print("⚠️  Configuration incomplete\n")
        print("SETUP INSTRUCTIONS:")
        print("1. Copy .env.template to .env")
        print("2. Edit .env and add:")
        print("   - GROQ_API_KEY (get from https://console.groq.com/keys)")
        print("   - SENDER_EMAIL (your Gmail)")
        print("   - SENDER_PASSWORD (Gmail App Password)")
        print()
    
    if deps_ok:
        print("✅ All dependencies installed\n")
    else:
        print("❌ Dependencies missing\n")
        print("INSTALL DEPENDENCIES:")
        print("pip install -r requirements.txt\n")
    
    if files_ok and config_ok and deps_ok:
        print("="*60)
        print("✨ SYSTEM IS READY TO RUN! ✨")
        print("="*60)
        print("\nStart the application:")
        print("  Windows: run_streamlit.bat")
        print("  Linux/Mac: bash run_streamlit.sh")
        print("  Manual: streamlit run streamlit_app.py")
        print("\nThe app will open at: http://localhost:8501\n")
        return 0
    else:
        print("="*60)
        print("⚠️  SYSTEM IS NOT READY")
        print("="*60)
        print("\nFix the issues above and try again.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
