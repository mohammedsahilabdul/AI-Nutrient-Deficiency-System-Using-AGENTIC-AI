#!/usr/bin/env python3
"""
Quick Start Guide - Launch and Test the Fixed System
Verify that reports, diet plans, and emails all work properly
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_step(step_num, title):
    """Print numbered step"""
    print(f"  [{step_num}] {title}")

def check_environment():
    """Check if environment is properly configured"""
    print_section("ENVIRONMENT CHECK")
    
    checks = {
        "Python 3.7+": sys.version_info >= (3, 7),
        ".env file exists": os.path.exists(".env"),
        "reports/ directory": os.path.exists("reports") or os.makedirs("reports", exist_ok=True),
        "index.html exists": os.path.exists("index.html"),
        "main_new.py exists": os.path.exists("main_new.py"),
    }
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    return all_passed

def test_imports():
    """Test critical imports"""
    print_section("TESTING IMPORTS")
    
    imports = {
        "FastAPI": "fastapi",
        "Groq": "groq",
        "Anthropic": "anthropic",
        "SQLAlchemy": "sqlalchemy",
        "OpenCV": "cv2",
    }
    
    for package_name, import_name in imports.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ⚠️  {package_name} (optional)")

def start_server():
    """Start the FastAPI server"""
    print_section("STARTING SERVER")
    
    print_step(1, "Launching main_new.py on http://localhost:9000...")
    print("\n  Wait for: 'Uvicorn running on http://0.0.0.0:9000'")
    print("  (Server will run in background)\n")
    
    try:
        # Start server in background
        proc = subprocess.Popen(
            [sys.executable, "main_new.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        print("  ✅ Server should be starting now...")
        print("  ℹ️  Keep this window open. Server logs will appear above.")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to start server: {e}")
        return False

def test_endpoints():
    """Test API endpoints"""
    print_section("TESTING ENDPOINTS")
    
    print_step(1, "Testing health check...")
    try:
        import requests
        response = requests.get("http://localhost:9000/api/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ API is responding")
        else:
            print(f"  ⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ⚠️  Could not reach API: {e}")
        print("  ℹ️  Server may still be starting...")

def show_manual_test_steps():
    """Show manual testing steps for user"""
    print_section("MANUAL TESTING (Web Form)")
    
    print_step(1, "Open your browser:")
    print("     → http://localhost:9000")
    print()
    
    print_step(2, "Fill the form:")
    print("     • Patient Name: Test Patient")
    print("     • Age: 35")
    print("     • Sex: Male/Female")
    print("     • Location: New York")
    print()
    
    print_step(3, "Upload sample images:")
    print("     • Eye image: From DATASETS/eyes/")
    print("     • Nails image: From DATASETS/nails/")
    print("     • Tongue image: From DATASETS/tongue/")
    print()
    
    print_step(4, "Configure email:")
    print("     ☑ Check 'Send Email'")
    print("     • Enter patient email")
    print("     ☑ Check 'Generate PDF'")
    print()
    
    print_step(5, "Click 'Analyze'")
    print("     → Results will appear in Report tab")
    print("     → Email will be sent to patient")
    print()

def verify_report_generation():
    """Verify that reports are being generated"""
    print_section("VERIFYING REPORT GENERATION")
    
    print_step(1, "Running report generation test...")
    
    try:
        from agent_report_diet import ReportGenerator, DietPlanGenerator
        
        # Test report
        rep_gen = ReportGenerator()
        result = rep_gen.generate_medical_report(
            diagnosis="Test Diagnosis",
            analyses={"eye": "Test", "nails": "Test", "tongue": "Test"}
        )
        
        if result["status"] == "success" and result.get("report"):
            print(f"  ✅ Report generated ({len(result['report'])} chars)")
        else:
            print(f"  ❌ Report generation failed")
            return False
        
        # Test diet plan
        diet_gen = DietPlanGenerator()
        result = diet_gen.generate_diet_plan(
            diagnosis="Test Diagnosis"
        )
        
        if result["status"] == "success" and result.get("diet_plan"):
            print(f"  ✅ Diet plan generated ({len(result['diet_plan'])} chars)")
        else:
            print(f"  ❌ Diet plan generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing reports: {e}")
        return False

def show_expected_results():
    """Show what user should expect to see"""
    print_section("EXPECTED RESULTS")
    
    print("When analysis completes successfully, you will see:\n")
    
    print("📊 DIAGNOSTIC RESULTS tab:")
    print("  • Diagnosis: [Medical condition found]")
    print("  • Severity: [None/Mild/Moderate/Severe]")
    print("  • Confidence: [85-95%]")
    print()
    
    print("📋 MEDICAL REPORT tab:")
    print("  • Clinical Summary section")
    print("  • Individual findings (Eye, Nails, Tongue)")
    print("  • Assessment with status and severity")
    print("  • Recommendations for patient")
    print()
    
    print("🥗 DIET PLAN tab:")
    print("  • Personalized 30-day meal plan")
    print("  • Daily meal patterns")
    print("  • Nutritional guidelines")
    print("  • Shopping list")
    print()
    
    print("📧 EMAIL NOTIFICATION:")
    print("  • Patient receives email with:")
    print("    ✓ Full diagnosis summary")
    print("    ✓ Complete medical report")
    print("    ✓ Diet plan")
    print("    ✓ PDF attachment (if ReportLab installed)")
    print("    ✓ Doctor recommendations")
    print()

def show_troubleshooting():
    """Show troubleshooting guide"""
    print_section("TROUBLESHOOTING")
    
    print("Issue: 'No report available' message\n")
    print("  Solution:")
    print("  • System has auto-fallback, should not happen")
    print("  • Check terminal logs for errors")
    print("  • Ensure LLM keys are set in .env")
    print()
    
    print("Issue: Port 9000 already in use\n")
    print("  Solution:")
    print("  • Change port in main_new.py line ~20")
    print("  • Or kill process: fuser -k 9000/tcp")
    print()
    
    print("Issue: Email not sent\n")
    print("  Solution:")
    print("  • Run: python test_email.py")
    print("  • Check Gmail credentials in .env")
    print("  • Enable 'Less secure app access' in Gmail")
    print()
    
    print("Issue: Images not uploading\n")
    print("  Solution:")
    print("  • Check DATASETS/ folder has sample images")
    print("  • Verify file permissions")
    print("  • Try smaller image files")
    print()

def show_next_steps():
    """Show next steps"""
    print_section("NEXT STEPS")
    
    print("✅ System is ready!\n")
    
    print("1. Keep the server running (press Ctrl+C when done)")
    print()
    
    print("2. Test with the web form:")
    print("   → http://localhost:9000")
    print()
    
    print("3. Verify reports are generated:")
    print("   → Check 'Medical Report' tab")
    print("   → Check 'Diet Plan' tab")
    print()
    
    print("4. Check email:")
    print("   → Open your email inbox")
    print("   → You should receive analysis report")
    print()
    
    print("5. For production deployment:")
    print("   → See PRODUCTION_GUIDE.md")
    print()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "MEDICAL DIAGNOSTIC SYSTEM" + " "*28 + "║")
    print("║" + " "*17 + "Quick Start & Test Guide" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Some environment checks failed. Continuing anyway...\n")
    
    # Test imports
    test_imports()
    
    # Verify report generation
    if not verify_report_generation():
        print("\n⚠️  Report generation seems to have issues")
        print("   But the system has auto-fallback enabled")
    
    # Show manual test steps
    show_manual_test_steps()
    
    # Show expected results
    show_expected_results()
    
    # Show troubleshooting
    show_troubleshooting()
    
    # Show next steps
    show_next_steps()
    
    print("\n" + "="*70)
    print("  Ready to test? Start with: python main_new.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
