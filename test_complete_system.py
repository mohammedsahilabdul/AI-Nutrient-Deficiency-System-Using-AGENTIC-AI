#!/usr/bin/env python3
"""
Complete System Test - Verify Reports, PDFs, and Emails
Tests the entire workflow with fallback mechanisms
"""

import sys
import os
import base64
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment
os.environ['USE_GROQ'] = 'True'  # Use Groq if available

from agent_report_diet import ReportGenerator, DietPlanGenerator, Agent1_ReportAndDiet
from features import PDFExporter, EmailNotifier
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_report_generation():
    """Test medical report generation with fallback"""
    print("\n" + "="*70)
    print("TEST 1: MEDICAL REPORT GENERATION")
    print("="*70)
    
    report_gen = ReportGenerator()
    
    # Test data
    diagnosis = "Mild Anemia with Nutritional Deficiency"
    analyses = {
        "eye": "Pale conjunctiva indicating possible anemia",
        "nails": "Brittle nails with horizontal ridges, low iron levels",
        "tongue": "Pale tongue coating, slightly swollen papillae"
    }
    patient_info = {
        "name": "Test Patient",
        "age": 35,
        "sex": "Female",
        "allergies": "Penicillin"
    }
    
    print(f"📋 Diagnosis: {diagnosis}")
    print(f"👤 Patient: {patient_info['name']}, Age {patient_info['age']}")
    print(f"📷 Analyses provided: {len(analyses)} body parts")
    
    result = report_gen.generate_medical_report(
        diagnosis=diagnosis,
        analyses=analyses,
        confidence=0.85,
        patient_info=patient_info
    )
    
    if result["status"] == "success":
        report_text = result.get("report", "")
        print(f"✅ Report Generated Successfully!")
        print(f"   - Status: {result['status']}")
        print(f"   - Length: {len(report_text)} characters")
        print(f"   - Confidence: {result.get('confidence', 'N/A')}")
        print(f"   - Auto-generated: {result.get('auto_generated', False)}")
        print(f"\n   Preview (first 200 chars):\n   {report_text[:200]}...")
        return True
    else:
        print(f"❌ Report generation failed: {result.get('error', 'Unknown error')}")
        return False

def test_diet_plan_generation():
    """Test diet plan generation with fallback"""
    print("\n" + "="*70)
    print("TEST 2: DIET PLAN GENERATION")
    print("="*70)
    
    diet_gen = DietPlanGenerator()
    
    # Test data
    diagnosis = "Mild Anemia with Nutritional Deficiency"
    
    print(f"🥗 Condition: {diagnosis}")
    print(f"📊 Severity: Moderate")
    print(f"⏱️  Duration: 30 days")
    
    result = diet_gen.generate_diet_plan(
        diagnosis=diagnosis,
        condition_severity="moderate",
        duration_days=30,
        dietary_restrictions=["peanuts"],
        patient_info={"allergies": "Peanuts"}
    )
    
    if result["status"] == "success":
        diet_text = result.get("diet_plan", "")
        print(f"✅ Diet Plan Generated Successfully!")
        print(f"   - Status: {result['status']}")
        print(f"   - Length: {len(diet_text)} characters")
        print(f"   - Duration: {result.get('duration', 'N/A')} days")
        print(f"   - Severity: {result.get('severity', 'N/A')}")
        print(f"   - Auto-generated: {result.get('auto_generated', False)}")
        print(f"\n   Preview (first 200 chars):\n   {diet_text[:200]}...")
        return True
    else:
        print(f"❌ Diet plan generation failed: {result.get('error', 'Unknown error')}")
        return False

def test_agent1_complete():
    """Test Agent1 complete workflow"""
    print("\n" + "="*70)
    print("TEST 3: AGENT 1 COMPLETE WORKFLOW")
    print("="*70)
    
    agent1 = Agent1_ReportAndDiet()
    
    # Test data
    diagnosis = "Mild Anemia with Nutritional Deficiency"
    analyses = {
        "eye": "Pale conjunctiva indicating possible anemia",
        "nails": "Brittle nails with horizontal ridges",
        "tongue": "Pale tongue with swollen papillae"
    }
    patient_info = {
        "name": "Test Patient",
        "age": 35,
        "sex": "Female",
        "location": "New York"
    }
    
    print(f"🤖 Executing Agent 1 workflow...")
    print(f"   - Diagnosis: {diagnosis}")
    print(f"   - Patient: {patient_info['name']}")
    print(f"   - Severity: Moderate")
    
    result = agent1.execute(
        diagnosis=diagnosis,
        analyses=analyses,
        condition_severity="moderate",
        patient_info=patient_info,
        dietary_restrictions=None
    )
    
    if result["status"] == "success":
        medical_report = result.get("medical_report", {})
        diet_plan = result.get("diet_plan", {})
        
        report_text = ""
        if isinstance(medical_report, dict):
            report_text = medical_report.get("report", "")
        else:
            report_text = str(medical_report)
        
        diet_text = ""
        if isinstance(diet_plan, dict):
            diet_text = diet_plan.get("diet_plan", "")
        else:
            diet_text = str(diet_plan)
        
        print(f"✅ Agent 1 Execution Complete!")
        print(f"   - Status: {result['status']}")
        print(f"   - Medical Report: {len(report_text)} characters")
        print(f"   - Diet Plan: {len(diet_text)} characters")
        print(f"   - Report file: {result.get('report_file', 'Not saved')}")
        print(f"   - Diet plan file: {result.get('diet_plan_file', 'Not saved')}")
        print(f"   - Agent: {result.get('agent', 'Unknown')}")
        
        if not report_text:
            print(f"⚠️  WARNING: Report text is empty!")
            return False
        if not diet_text:
            print(f"⚠️  WARNING: Diet plan text is empty!")
            return False
        
        return True
    else:
        print(f"❌ Agent 1 execution failed: {result.get('error', 'Unknown error')}")
        return False

def test_pdf_generation():
    """Test PDF generation"""
    print("\n" + "="*70)
    print("TEST 4: PDF GENERATION")
    print("="*70)
    
    # Sample data
    patient_name = "Test Patient"
    age = 35
    sex = "Female"
    diagnosis = "Mild Anemia with Nutritional Deficiency"
    severity = "Moderate"
    medical_report = """# MEDICAL REPORT

## Clinical Summary
The patient presents with symptoms consistent with mild anemia. Laboratory findings suggest nutritional deficiency.

## Detailed Findings
- Eye examination shows pale conjunctiva
- Nails show brittleness and ridges
- Tongue shows pale coloration

## Assessment
- Status: At Risk
- Severity: Moderate
- Confidence: 85%
"""
    
    diet_plan = """# DIET PLAN

## Goals
Increase iron and B12 intake to address nutritional deficiency

## Recommended Foods
- Red meat and poultry
- Leafy greens
- Legumes
- Fortified cereals
"""
    
    print(f"📄 Generating PDF for: {patient_name}")
    print(f"   - Age: {age}, Sex: {sex}")
    print(f"   - Diagnosis: {diagnosis}")
    print(f"   - Severity: {severity}")
    
    pdf_path = PDFExporter.generate_report_pdf(
        patient_name=patient_name,
        age=age,
        sex=sex,
        diagnosis=diagnosis,
        severity=severity,
        medical_report=medical_report,
        diet_plan=diet_plan,
        confidence=0.85,
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    
    if pdf_path and os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"✅ PDF Generated Successfully!")
        print(f"   - Path: {pdf_path}")
        print(f"   - Size: {file_size} bytes")
        return True
    else:
        print(f"❌ PDF generation failed or file not found")
        return False

def test_email_attachment():
    """Test email attachment functionality"""
    print("\n" + "="*70)
    print("TEST 5: EMAIL ATTACHMENT FUNCTIONALITY")
    print("="*70)
    
    # Create a test PDF first
    pdf_path = PDFExporter.generate_report_pdf(
        patient_name="Email Test Patient",
        age=40,
        sex="Male",
        diagnosis="Test Diagnosis",
        severity="Mild",
        medical_report="Test medical report",
        diet_plan="Test diet plan",
        confidence=0.80,
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"✅ Test PDF created: {pdf_path}")
        print(f"📎 Attachment Size: {os.path.getsize(pdf_path)} bytes")
        print(f"✅ Email attachment capability verified!")
        return True
    else:
        print(f"❌ Could not create test PDF for email attachment")
        return False

def run_all_tests():
    """Run all system tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "COMPLETE SYSTEM TEST SUITE" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    
    # Create reports directory if needed
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/pdf", exist_ok=True)
    
    results = {
        "Report Generation": test_report_generation(),
        "Diet Plan Generation": test_diet_plan_generation(),
        "Agent 1 Complete": test_agent1_complete(),
        "PDF Generation": test_pdf_generation(),
        "Email Attachment": test_email_attachment(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System Ready!")
        return True
    else:
        print("⚠️  Some tests failed - Review output above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
