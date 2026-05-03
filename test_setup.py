"""
Test script to verify AI Medical Diagnostic System setup
Run this after installation to check all components
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}\n")

def check_python():
    print_header("Python Version Check")
    print(f"✓ Python {sys.version}")
    
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required!")
        return False
    
    print("✓ Python version OK")
    return True

def check_directories():
    print_header("Directory Structure Check")
    
    required_dirs = [
        'uploads',
        'reports',
        'logs',
        'cache',
        'memory',
        'DATASETS'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ {directory}/")
        else:
            print(f"✗ {directory}/ (missing)")
            os.makedirs(directory, exist_ok=True)
            print(f"  → Created")
    
    return True

def check_files():
    print_header("Required Files Check")
    
    required_files = [
        'config.py',
        'image_processor.py',
        'vision_agent.py',
        'agent_report_diet.py',
        'agent_hospital_doctor.py',
        'main.py',
        'index.html',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (missing)")
            all_exist = False
    
    return all_exist

def check_dependencies():
    print_header("Python Dependencies Check")
    
    dependencies = [
        'fastapi',
        'uvicorn',
        'groq',  # Groq API library
        'anthropic',
        'cv2',  # opencv-python
        'PIL',  # pillow
        'numpy',
        'requests',
        'pydantic',
        'dotenv'
    ]
    
    all_installed = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} (not installed)")
            all_installed = False
    
    return all_installed

def check_environment():
    print_header("Environment Variables Check")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✓ .env file exists")
        
        # Try to load it
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check which provider is being used
            use_groq = os.getenv('USE_GROQ', 'true').lower() == 'true'
            
            if use_groq:
                groq_key = os.getenv('GROQ_API_KEY')
                if groq_key and groq_key != 'your_groq_api_key_here':
                    print("✓ GROQ_API_KEY configured (primary)")
                    return True
                else:
                    print("⚠ GROQ_API_KEY not configured (required if USE_GROQ=true)")
                    return False
            else:
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if api_key and api_key != 'your_claude_api_key_here':
                    print("✓ ANTHROPIC_API_KEY configured (primary)")
                    return True
                else:
                    print("⚠ ANTHROPIC_API_KEY not configured (required if USE_GROQ=false)")
                    return False
        
        except Exception as e:
            print(f"✗ Error loading .env: {e}")
            return False
    else:
        print("✗ .env file not found")
        print("  → Run: cp .env.example .env")
        print("  → Then edit .env with your API keys")
        return False

def check_api_key():
    print_header("API Keys Verification")
    
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        use_groq = os.getenv('USE_GROQ', 'true').lower() == 'true'
        
        if use_groq:
            groq_key = os.getenv('GROQ_API_KEY')
            if not groq_key or groq_key == 'your_groq_api_key_here':
                print("⚠ GROQ_API_KEY not set")
                print("  To use Groq API (Free & Fast):")
                print("  1. Get key from https://console.groq.com/keys")
                print("  2. Add to .env: GROQ_API_KEY=your_key")
                return False
            print("✓ GROQ_API_KEY set")
        else:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key or api_key == 'your_claude_api_key_here':
                print("⚠ ANTHROPIC_API_KEY not set")
                print("  To use Claude API:")
                print("  1. Get key from https://console.anthropic.com")
                print("  2. Add to .env: ANTHROPIC_API_KEY=your_key")
                return False
            print("✓ ANTHROPIC_API_KEY set")
        
        # Don't actually test the API key to avoid usage
        print("⚠ Not testing API key (to avoid charges)")
        print("  API will be tested when you run the application")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_imports():
    print_header("Module Imports Test")
    
    modules = [
        ('config', 'Configuration'),
        ('image_processor', 'Image Processor'),
        ('vision_agent', 'Vision Agent'),
        ('agent_report_diet', 'Report & Diet Agent'),
        ('agent_hospital_doctor', 'Hospital & Doctor Agent'),
    ]
    
    all_success = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name} ({module_name})")
        except Exception as e:
            print(f"✗ {display_name} ({module_name}): {e}")
            all_success = False
    
    return all_success

def main():
    print("\n")
    print("╔═════════════════════════════════════════════════╗")
    print("║  AI Medical Diagnostic System - Setup Test     ║")
    print("║  Version 1.0.0                                 ║")
    print("╚═════════════════════════════════════════════════╝")
    
    checks = [
        ("Python Version", check_python),
        ("Directories", check_directories),
        ("Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("API Keys", check_api_key),
        ("Module Imports", test_imports),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"✗ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print_header("✅ All Checks Passed!")
        print("System is ready to use!")
        print("\nNext steps:")
        print("1. Run the backend: python main.py")
        print("2. Open index.html in your browser")
        print("3. Upload medical images for analysis")
        return 0
    else:
        print_header("⚠️ Some Checks Failed")
        print("Please fix the issues above before running the system")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
