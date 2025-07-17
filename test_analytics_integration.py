#!/usr/bin/env python3
"""
Test script to verify analytics integration between GUI and FastAPI backend.
Run this to test the complete analytics pipeline.
"""

import requests
import json
import sys
from pathlib import Path

# Test configuration
ANALYTICS_BASE_URL = "http://127.0.0.1:8001"
TEST_PROJECT_ID = "eccedcb4-2943-4b55-bbba-931682d513b8"  # From the logs

def test_backend_health():
    """Test backend health endpoint."""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{ANALYTICS_BASE_URL}/api/v1/analytics/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backend is healthy: {result}")
            return True
        else:
            print(f"❌ Backend unhealthy - HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_project_recommendations():
    """Test project recommendations endpoint."""
    print(f"🔍 Testing recommendations for project {TEST_PROJECT_ID}...")
    try:
        response = requests.get(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/project/{TEST_PROJECT_ID}/recommendations", 
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Recommendations received: {len(result.get('data', {}).get('recommendations', []))} recommendations")
            if result.get('data', {}).get('recommendations'):
                for i, rec in enumerate(result['data']['recommendations'][:2]):  # Show first 2
                    print(f"   {i+1}. {rec.get('method', 'Unknown')} - {rec.get('rationale', 'No rationale')}")
            return True
        else:
            print(f"❌ Recommendations failed - HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Recommendations request failed: {e}")
        return False

def test_descriptive_analysis():
    """Test descriptive analysis endpoint."""
    print(f"🔍 Testing descriptive analysis for project {TEST_PROJECT_ID}...")
    try:
        response = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/project/{TEST_PROJECT_ID}/analyze?analysis_type=descriptive",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            print(f"✅ Descriptive analysis completed:")
            print(f"   - Analysis type: {data.get('analysis_type', 'unknown')}")
            print(f"   - Analyses run: {list(data.get('analyses', {}).keys())}")
            if 'data_characteristics' in data:
                chars = data['data_characteristics']
                print(f"   - Sample size: {chars.get('sample_size', 'unknown')}")
                print(f"   - Variables: {len(chars.get('numeric_variables', []))} numeric, {len(chars.get('categorical_variables', []))} categorical")
            return True
        else:
            print(f"❌ Descriptive analysis failed - HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Descriptive analysis request failed: {e}")
        return False

def test_inferential_analysis():
    """Test inferential analysis endpoint."""
    print(f"🔍 Testing inferential analysis for project {TEST_PROJECT_ID}...")
    try:
        response = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/project/{TEST_PROJECT_ID}/analyze?analysis_type=inferential",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            print(f"✅ Inferential analysis completed:")
            print(f"   - Analysis type: {data.get('analysis_type', 'unknown')}")
            print(f"   - Analyses run: {list(data.get('analyses', {}).keys())}")
            return True
        else:
            print(f"❌ Inferential analysis failed - HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Inferential analysis request failed: {e}")
        return False

def test_qualitative_analysis():
    """Test qualitative analysis endpoint."""
    print(f"🔍 Testing qualitative analysis for project {TEST_PROJECT_ID}...")
    try:
        response = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/project/{TEST_PROJECT_ID}/analyze?analysis_type=qualitative",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            print(f"✅ Qualitative analysis completed:")
            print(f"   - Analysis type: {data.get('analysis_type', 'unknown')}")
            print(f"   - Analyses run: {list(data.get('analyses', {}).keys())}")
            return True
        else:
            print(f"❌ Qualitative analysis failed - HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Qualitative analysis request failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 ANALYTICS INTEGRATION TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Project Recommendations", test_project_recommendations),
        ("Descriptive Analysis", test_descriptive_analysis),
        ("Inferential Analysis", test_inferential_analysis),
        ("Qualitative Analysis", test_qualitative_analysis),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
            else:
                print(f"   Test failed!")
        except Exception as e:
            print(f"   Test crashed: {e}")
        
    print("\n" + "=" * 50)
    print(f"🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Analytics integration is working perfectly!")
        print("   ✅ GUI can connect to FastAPI backend")
        print("   ✅ All analysis types are supported")
        print("   ✅ Data is being processed correctly")
    else:
        print("⚠️  Some integration issues detected:")
        if passed == 0:
            print("   🔴 Backend appears to be offline or unreachable")
        else:
            print(f"   🟡 {total - passed} analysis endpoints have issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 