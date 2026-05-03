#!/usr/bin/env python3
"""
Quick test script to verify the Agentic Medical System is working
Run this after starting: python main_new.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_health():
    """Test if server is running"""
    print_section("1️⃣  TESTING SERVER HEALTH")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Server is running!")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Server is NOT running: {e}")
        print("Start the server with: python main_new.py")
        return False

def test_demo():
    """Test demo endpoint (no image upload needed)"""
    print_section("2️⃣  TESTING DEMO ANALYSIS (No Images Needed)")
    
    try:
        print("Testing diagnosis types...")
        
        for diagnosis_type in ["anemia", "diabetes", "infection", "normal"]:
            print(f"\n  Testing: {diagnosis_type.upper()}...")
            response = requests.post(
                f"{BASE_URL}/api/demo-analysis",
                params={"diagnosis_type": diagnosis_type}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ Status: {data.get('status')}")
                print(f"    ✅ Diagnosis: {data.get('diagnosis', 'N/A')[:100]}...")
                print(f"    ✅ Severity: {data.get('severity')}")
                print(f"    ✅ Workflow ID: {data.get('workflow_id')}")
            else:
                print(f"    ❌ Error: {response.status_code}")
        
        print("\n✅ All demo tests passed!")
        return True
    except Exception as e:
        print(f"❌ Demo test failed: {e}")
        return False

def test_endpoints():
    """List all available endpoints"""
    print_section("3️⃣  AVAILABLE ENDPOINTS")
    
    endpoints = {
        "🏥 MAIN AGENTIC WORKFLOW": [
            "POST /api/complete-analysis (requires 3 images + patient info)",
            "POST /api/analyze (alias - same as complete-analysis)",
        ],
        "🧪 DEMO (No Images)": [
            "POST /api/demo-analysis?diagnosis_type=anemia",
        ],
        "🔍 INDIVIDUAL AGENTS": [
            "POST /api/vision-analysis (image analysis only)",
            "POST /api/report-diet (report generation only)",
            "POST /api/healthcare-discovery (hospital search only)",
        ],
        "📊 MONITORING": [
            "GET /health (server health)",
            "GET /api/agents/status (agent statuses)",
            "GET /api/workflows (all analyses)",
            "GET /api/workflows/{id} (specific analysis)",
            "GET /api/info (system info)",
            "POST /api/reset (reset system)",
            "GET /test (ping test)",
        ]
    }
    
    for category, eps in endpoints.items():
        print(f"\n{category}")
        for ep in eps:
            print(f"  • {ep}")

def test_api_docs():
    """Tell user how to access interactive docs"""
    print_section("4️⃣  INTERACTIVE API DOCUMENTATION")
    
    print("Open in browser:")
    print(f"  🌐 Swagger UI:  {BASE_URL}/docs")
    print(f"  🌐 ReDoc:       {BASE_URL}/redoc")
    print(f"  🌐 Frontend:    {BASE_URL}/")
    print("\n✅ Use these to test endpoints interactively!")

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "🏥 AGENTIC MEDICAL SYSTEM TEST SUITE" + " "*16 + "║")
    print("╚" + "="*68 + "╝")
    
    # Test 1: Health
    if not test_health():
        print("\n❌ Server is not running!")
        print("Start with: python main_new.py")
        return False
    
    time.sleep(1)
    
    # Test 2: Demo
    if not test_demo():
        print("\n⚠️  Demo tests failed")
    
    # Test 3: Endpoints
    test_endpoints()
    
    # Test 4: Docs
    test_api_docs()
    
    # Summary
    print_section("✅ SYSTEM READY!")
    print("""
For complete medical analysis:

Step 1: Go to http://localhost:8000/docs
Step 2: Find: POST /api/complete-analysis
Step 3: Upload 3 images (eye, nails, tongue)
Step 4: Fill patient info
Step 5: Click Execute
Step 6: Wait ~20-30 seconds
Step 7: Get complete diagnosis + reports + doctors!

OR test demo first:

Step 1: Go to http://localhost:8000/docs
Step 2: Find: POST /api/demo-analysis
Step 3: Select diagnosis_type (anemia, diabetes, etc.)
Step 4: Click Execute
Step 5: See response structure (instant!)
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
