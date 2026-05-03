"""
Test Script for Production System Verification
Verifies all new features are working
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def print_test(name, result, details=""):
    """Print test result"""
    status = "✅" if result else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

def test_health():
    """Test health endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print_test("1. Health Check", resp.status_code == 200, f"Status: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print_test("1. Health Check", False, f"Error: {str(e)}")
        return False

def test_demo():
    """Test demo endpoint"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/demo-analysis?diagnosis_type=anemia",
            headers=HEADERS,
            timeout=10
        )
        success = resp.status_code == 200
        data = resp.json() if success else {}
        print_test("2. Demo Analysis", success, f"Status: {resp.status_code}, Diagnosis: {data.get('diagnosis', 'N/A')}")
        return success
    except Exception as e:
        print_test("2. Demo Analysis", False, f"Error: {str(e)}")
        return False

def test_agents_status():
    """Test agents status"""
    try:
        resp = requests.get(f"{BASE_URL}/api/agents/status", headers=HEADERS, timeout=5)
        success = resp.status_code == 200
        print_test("3. Agents Status", success, f"Status: {resp.status_code}")
        if success:
            print(f"   Agents: {list(resp.json().get('agents', {}).keys())}")
        return success
    except Exception as e:
        print_test("3. Agents Status", False, f"Error: {str(e)}")
        return False

def test_system_info():
    """Test system info"""
    try:
        resp = requests.get(f"{BASE_URL}/api/info", headers=HEADERS, timeout=5)
        success = resp.status_code == 200
        data = resp.json() if success else {}
        print_test("4. System Info", success, f"Status: {resp.status_code}")
        if success and data.get("features"):
            features = data["features"]
            print(f"   PDF Export: {'✅' if features.get('pdf_export') else '❌'}")
            print(f"   Email: {'✅' if features.get('email') else '❌'}")
            print(f"   Database: {'✅' if features.get('database') else '❌'}")
            print(f"   Auth: {'✅' if features.get('auth') else '❌'}")
            print(f"   Cache: {'✅' if features.get('cache') else '❌'}")
        return success
    except Exception as e:
        print_test("4. System Info", False, f"Error: {str(e)}")
        return False

def test_database():
    """Test database"""
    try:
        from database import init_db, DatabaseStats, SessionLocal
        init_db()
        db = SessionLocal()
        stats = DatabaseStats.get_stats(db)
        print_test("5. Database", True, f"Patients: {stats.get('total_patients', 0)}")
        db.close()
        return True
    except Exception as e:
        print_test("5. Database", False, f"Error: {str(e)}")
        return False

def test_auth():
    """Test authentication"""
    try:
        from auth import APIKeyManager, init_auth
        init_auth()
        keys = APIKeyManager.list_keys()
        print_test("6. Authentication", len(keys) > 0, f"API Keys: {len(keys)}")
        return len(keys) > 0
    except Exception as e:
        print_test("6. Authentication", False, f"Error: {str(e)}")
        return False

def test_features():
    """Test features"""
    try:
        from features import PDFExporter, CacheManager, init_features
        init_features()
        
        # Test cache
        CacheManager.init_cache()
        cache_size = CacheManager.get_cache_size()
        
        print_test("7. Features", True, f"PDF Available: {PDFExporter.PDF_AVAILABLE}, Cache Size: {cache_size:.2f}MB")
        return True
    except Exception as e:
        print_test("7. Features", False, f"Error: {str(e)}")
        return False

def test_orchestrator():
    """Test orchestrator"""
    try:
        from agent_orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        print_test("8. Orchestrator", orch is not None, "Orchestrator initialized")
        return True
    except Exception as e:
        print_test("8. Orchestrator", False, f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 PRODUCTION SYSTEM VERIFICATION")
    print("="*60 + "\n")
    
    results = {
        "health": test_health(),
        "demo": test_demo(),
        "agents": test_agents_status(),
        "info": test_system_info(),
        "database": test_database(),
        "auth": test_auth(),
        "features": test_features(),
        "orchestrator": test_orchestrator()
    }
    
    print("\n" + "="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - System is ready!")
    else:
        print("⚠️  Some tests failed - Check errors above")
    
    print("="*60 + "\n")
    
    # API Documentation
    print("📚 API DOCUMENTATION:")
    print(f"   📖 Swagger UI: {BASE_URL}/docs")
    print(f"   📖 ReDoc: {BASE_URL}/redoc")
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Open {BASE_URL}/docs in browser")
    print(f"   2. Try /api/demo-analysis endpoint (no images needed)")
    print(f"   3. Upload real medical images to /api/complete-analysis")
    print(f"   4. Review PRODUCTION_GUIDE.md for detailed instructions")
    print()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
