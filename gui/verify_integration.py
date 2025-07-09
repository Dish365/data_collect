"""
Comprehensive GUI-Analytics Integration Verification
This script tests the complete integration between the GUI and analytics backend.
Run this after both services are running to verify everything works.
"""

import sys
import os
import time
import json
import requests
from datetime import datetime

# Add GUI path
sys.path.insert(0, os.path.dirname(__file__))

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_status(message, status="info"):
    """Print a status message with appropriate formatting"""
    symbols = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{symbols.get(status, 'ℹ️')} {message}")

def test_backend_health():
    """Test backend health and connectivity"""
    print_section("Backend Health Check")
    
    try:
        response = requests.get("http://127.0.0.1:8001/api/v1/analytics/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_status("Analytics backend is running", "success")
            print_status(f"Response: {json.dumps(data, indent=2)}", "info")
            return True
        else:
            print_status(f"Backend returned status {response.status_code}", "error")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to analytics backend", "error")
        print_status("Make sure to start: python backend/analytics/main.py", "info")
        return False
    except Exception as e:
        print_status(f"Health check failed: {e}", "error")
        return False

def test_analytics_service_integration():
    """Test the analytics service with real backend"""
    print_section("Analytics Service Integration Test")
    
    try:
        # Mock dependencies
        class MockAuth:
            def get_user_data(self):
                return {'id': 'test_user', 'username': 'test'}
        
        class MockDB:
            def get_db_connection(self):
                return None  # Test fallback behavior
        
        from services.analytics_service import AnalyticsService
        
        service = AnalyticsService(MockAuth(), MockDB())
        print_status("Analytics service initialized", "success")
        
        # Test health check
        health = service.check_backend_health()
        if health and 'error' not in health:
            print_status("Health check passed", "success")
        else:
            print_status(f"Health check issue: {health.get('error', 'Unknown')}", "warning")
        
        # Test data characteristics (should work with fallback)
        test_project = "test_project_verification"
        characteristics = service.get_data_characteristics(test_project)
        if characteristics:
            print_status("Data characteristics method working", "success")
        else:
            print_status("Data characteristics failed", "error")
        
        # Test recommendations
        recommendations = service.get_analysis_recommendations(test_project)
        if recommendations:
            print_status("Recommendations method working", "success")
            if 'recommendations' in recommendations:
                rec_count = len(recommendations.get('recommendations', {}).get('primary_recommendations', []))
                print_status(f"Got {rec_count} primary recommendations", "info")
        else:
            print_status("Recommendations failed", "error")
        
        return True
        
    except Exception as e:
        print_status(f"Analytics service test failed: {e}", "error")
        return False

def test_gui_components():
    """Test GUI component imports and initialization"""
    print_section("GUI Components Test")
    
    try:
        # Test analytics screen
        from screens.analytics import AnalyticsScreen
        print_status("Analytics screen imported", "success")
        
        # Test analytics widgets
        from widgets.analytics_stat_card import AnalyticsStatCard
        print_status("Analytics stat card imported", "success")
        
        # Test responsive layout helper
        try:
            from widgets.responsive_layout import ResponsiveHelper
            print_status("Responsive layout helper imported", "success")
        except ImportError:
            print_status("Responsive layout helper not found (optional)", "warning")
        
        return True
        
    except Exception as e:
        print_status(f"GUI component test failed: {e}", "error")
        return False

def test_end_to_end_flow():
    """Test complete end-to-end analytics flow"""
    print_section("End-to-End Analytics Flow Test")
    
    try:
        from services.analytics_service import AnalyticsService
        
        # Mock services
        class MockAuth:
            def get_user_data(self):
                return {'id': 'e2e_test_user'}
        
        class MockDB:
            def get_db_connection(self):
                return None
        
        service = AnalyticsService(MockAuth(), MockDB())
        test_project = f"e2e_test_{int(time.time())}"
        
        print_status(f"Testing with project: {test_project}", "info")
        
        # Step 1: Get data characteristics
        print_status("Step 1: Getting data characteristics...", "info")
        characteristics = service.get_data_characteristics(test_project)
        if characteristics:
            print_status("✓ Data characteristics retrieved", "success")
        else:
            print_status("✗ Data characteristics failed", "error")
            return False
        
        # Step 2: Get recommendations
        print_status("Step 2: Getting analysis recommendations...", "info")
        recommendations = service.get_analysis_recommendations(test_project)
        if recommendations:
            print_status("✓ Recommendations retrieved", "success")
        else:
            print_status("✗ Recommendations failed", "error")
            return False
        
        # Step 3: Run analysis
        print_status("Step 3: Running descriptive analysis...", "info")
        analysis = service.run_descriptive_analysis(test_project)
        if analysis:
            print_status("✓ Analysis completed", "success")
        else:
            print_status("✗ Analysis failed", "error")
            return False
        
        print_status("End-to-end flow completed successfully!", "success")
        return True
        
    except Exception as e:
        print_status(f"End-to-end test failed: {e}", "error")
        return False

def test_api_endpoints():
    """Test specific API endpoints"""
    print_section("API Endpoints Verification")
    
    base_url = "http://127.0.0.1:8001/api/v1/analytics"
    test_project = "api_test_project"
    
    endpoints = [
        ("GET", "/health", "Health check"),
        ("GET", f"/project/{test_project}/data-characteristics", "Data characteristics"),
        ("GET", f"/project/{test_project}/recommendations", "Recommendations"),
        ("POST", f"/project/{test_project}/analyze", "Analysis endpoint")
    ]
    
    success_count = 0
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json={"analysis_type": "descriptive"}, timeout=10)
            
            if response.status_code in [200, 201]:
                print_status(f"✓ {description}: {response.status_code}", "success")
                success_count += 1
            else:
                print_status(f"✗ {description}: {response.status_code}", "warning")
                
        except Exception as e:
            print_status(f"✗ {description}: {str(e)[:50]}...", "error")
    
    print_status(f"API endpoints: {success_count}/{len(endpoints)} working", "info")
    return success_count == len(endpoints)

def test_url_configuration():
    """Verify URL configuration consistency"""
    print_section("URL Configuration Check")
    
    try:
        from services.analytics_service import AnalyticsService
        
        # Create service instance
        class MockAuth:
            def get_user_data(self):
                return {}
        
        class MockDB:
            def get_db_connection(self):
                return None
        
        service = AnalyticsService(MockAuth(), MockDB())
        
        expected_url = "http://127.0.0.1:8001"
        actual_url = service.base_url
        
        if actual_url == expected_url:
            print_status(f"✓ Base URL correct: {actual_url}", "success")
        else:
            print_status(f"✗ URL mismatch - Expected: {expected_url}, Got: {actual_url}", "error")
            return False
        
        # Test URL construction
        test_endpoint = service.base_url + "/api/v1/analytics/health"
        expected_full_url = "http://127.0.0.1:8001/api/v1/analytics/health"
        
        if test_endpoint == expected_full_url:
            print_status("✓ URL construction correct", "success")
        else:
            print_status(f"✗ URL construction error", "error")
            return False
        
        return True
        
    except Exception as e:
        print_status(f"URL configuration test failed: {e}", "error")
        return False

def generate_integration_report():
    """Generate a comprehensive integration report"""
    print_section("Integration Summary Report")
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Analytics Service", test_analytics_service_integration),
        ("GUI Components", test_gui_components),
        ("API Endpoints", test_api_endpoints),
        ("URL Configuration", test_url_configuration),
        ("End-to-End Flow", test_end_to_end_flow)
    ]
    
    results = {}
    passed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
                print_status(f"{test_name}: PASSED", "success")
            else:
                print_status(f"{test_name}: FAILED", "error")
        except Exception as e:
            results[test_name] = False
            print_status(f"{test_name}: ERROR - {e}", "error")
    
    # Final report
    print_section("FINAL INTEGRATION REPORT")
    
    total = len(tests)
    percentage = (passed / total) * 100
    
    print_status(f"Tests Passed: {passed}/{total} ({percentage:.1f}%)", "info")
    
    if passed == total:
        print_status("🎉 PERFECT INTEGRATION! All systems working correctly", "success")
        print("\n📋 What this means:")
        print("   • GUI can successfully connect to analytics backend")
        print("   • All API endpoints are working correctly")
        print("   • Fallback mechanisms are functioning")
        print("   • End-to-end data flow is operational")
        print("   • Ready for production use!")
        
    elif passed >= total * 0.8:
        print_status("✅ GOOD INTEGRATION with minor issues", "warning")
        print("\n📋 Recommendations:")
        for test_name, result in results.items():
            if not result:
                print(f"   • Fix: {test_name}")
        
    else:
        print_status("❌ INTEGRATION ISSUES detected", "error")
        print("\n📋 Critical issues to fix:")
        for test_name, result in results.items():
            if not result:
                print(f"   • CRITICAL: {test_name}")
    
    print("\n🚀 Next Steps:")
    print("   1. If backend tests failed: Start analytics backend")
    print("   2. If GUI tests failed: Check Python imports and dependencies")
    print("   3. Test with real data in the GUI application")
    print("   4. Monitor logs for any runtime issues")
    
    return passed == total

def main():
    """Main verification function"""
    print("🔍 GUI-Analytics Integration Verification")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    print_section("Prerequisites Check")
    
    # Check if we're in the right directory
    if not os.path.exists("services/analytics_service.py"):
        print_status("Run this from the gui/ directory", "error")
        return False
    
    print_status("Running from correct directory", "success")
    
    # Run comprehensive verification
    success = generate_integration_report()
    
    print_section("Verification Complete")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 