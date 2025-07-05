"""
Test script to verify analytics endpoints work correctly.
Run this to test the auto-detection endpoints implementation.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        # Test base detector imports
        from app.analytics.auto_detect.base_detector import (
            BaseAutoDetector, DataCharacteristics, AnalysisRecommendation, 
            AnalysisSuggestions, DataType, AnalysisConfidence
        )
        print("✓ Base detector imports successful")
        
        # Test individual auto-detection modules
        from app.analytics.descriptive.auto_detection import DescriptiveAutoDetector
        print("✓ Descriptive auto-detection import successful")
        
        from app.analytics.inferential.auto_detection import InferentialAutoDetector  
        print("✓ Inferential auto-detection import successful")
        
        from app.analytics.qualitative.auto_detection import QualitativeAutoDetector
        print("✓ Qualitative auto-detection import successful")
        
        # Test unified auto-detector
        from app.analytics.auto_detect import UnifiedAutoDetector
        print("✓ Unified auto-detector import successful")
        
        # Test endpoint imports
        from app.api.v1.endpoints import descriptive, inferential, qualitative, auto_detect
        print("✓ All endpoint imports successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_descriptive_auto_detection():
    """Test descriptive analytics auto-detection."""
    print("\nTesting descriptive auto-detection...")
    
    try:
        from app.analytics.descriptive.auto_detection import DescriptiveAutoDetector
        
        # Create sample data
        np.random.seed(42)
        data = pd.DataFrame({
            'numeric_var1': np.random.normal(100, 15, 50),
            'numeric_var2': np.random.exponential(2, 50),
            'categorical_var': np.random.choice(['A', 'B', 'C'], 50),
            'binary_var': np.random.choice([0, 1], 50)
        })
        
        detector = DescriptiveAutoDetector()
        
        # Test data characteristics detection
        characteristics = detector.detect_data_characteristics(data)
        print(f"✓ Data characteristics detected: {characteristics.n_observations} obs, {characteristics.n_variables} vars")
        
        # Test analysis suggestions
        suggestions = detector.suggest_analyses(data)
        print(f"✓ Analysis suggestions generated: {len(suggestions.primary_recommendations)} primary, {len(suggestions.secondary_recommendations)} secondary")
        
        # Test auto-configuration
        if suggestions.primary_recommendations:
            method = suggestions.primary_recommendations[0].method
            config = detector.auto_configure_analysis(method, data)
            print(f"✓ Auto-configuration successful for {method}")
        
        return True
        
    except Exception as e:
        print(f"✗ Descriptive auto-detection failed: {e}")
        return False

def test_inferential_auto_detection():
    """Test inferential analytics auto-detection."""
    print("\nTesting inferential auto-detection...")
    
    try:
        from app.analytics.inferential.auto_detection import InferentialAutoDetector
        
        # Create sample data
        np.random.seed(42)
        data = pd.DataFrame({
            'target': np.random.normal(100, 15, 30),
            'group': np.random.choice(['Group1', 'Group2'], 30),
            'continuous': np.random.normal(50, 10, 30)
        })
        
        detector = InferentialAutoDetector()
        
        # Test data characteristics detection
        characteristics = detector.detect_data_characteristics(data, 'target', 'group')
        print(f"✓ Data characteristics detected for inferential analysis")
        
        # Test analysis suggestions
        suggestions = detector.suggest_analyses(data, target_variable='target', grouping_variable='group')
        print(f"✓ Statistical test suggestions generated: {len(suggestions.primary_recommendations)} primary")
        
        # Test auto-configuration
        if suggestions.primary_recommendations:
            method = suggestions.primary_recommendations[0].method
            config = detector.auto_configure_analysis(method, characteristics)
            print(f"✓ Test auto-configuration successful for {method}")
        
        return True
        
    except Exception as e:
        print(f"✗ Inferential auto-detection failed: {e}")
        return False

def test_qualitative_auto_detection():
    """Test qualitative analytics auto-detection."""
    print("\nTesting qualitative auto-detection...")
    
    try:
        from app.analytics.qualitative.auto_detection import QualitativeAutoDetector
        
        # Create sample text data
        texts = [
            "I really enjoyed this product. It exceeded my expectations and I would definitely recommend it.",
            "The service was terrible. I waited for hours and nobody helped me.",
            "This is an interesting research topic that deserves more investigation.",
            "The results show a clear pattern in the data that supports our hypothesis.",
            "I think this approach has potential but needs more development."
        ]
        
        detector = QualitativeAutoDetector()
        
        # Test data type detection
        data_type = detector.detect_data_type(texts)
        print(f"✓ Data type detected: {data_type['primary_data_type']} (confidence: {data_type['confidence']:.2f})")
        
        # Test analysis suggestions  
        df = pd.DataFrame({'text': texts})
        suggestions = detector.suggest_analyses(df, texts=texts)
        print(f"✓ Analysis suggestions generated: {len(suggestions.primary_recommendations)} primary")
        
        # Test auto-configuration
        if suggestions.primary_recommendations:
            method = suggestions.primary_recommendations[0].method
            config = detector.auto_configure_analysis(texts, method)
            print(f"✓ Auto-configuration successful for {method}")
        
        return True
        
    except Exception as e:
        print(f"✗ Qualitative auto-detection failed: {e}")
        return False

def test_unified_auto_detector():
    """Test unified auto-detector."""
    print("\nTesting unified auto-detector...")
    
    try:
        from app.analytics.auto_detect import UnifiedAutoDetector
        
        # Create mixed data
        np.random.seed(42)
        data = pd.DataFrame({
            'numeric_var': np.random.normal(100, 15, 20),
            'category': np.random.choice(['A', 'B', 'C'], 20),
            'text_data': [
                f"This is sample text number {i} with various content." 
                for i in range(20)
            ]
        })
        
        detector = UnifiedAutoDetector()
        
        # Test comprehensive analysis
        results = detector.analyze_comprehensive_data(data, analysis_type="auto")
        print(f"✓ Comprehensive analysis completed")
        print(f"  - Modules used: {results['coordination']['modules_used']}")
        print(f"  - Module results: {len(results['module_results'])} modules")
        
        return True
        
    except Exception as e:
        print(f"✗ Unified auto-detector failed: {e}")
        return False

def test_endpoint_structure():
    """Test that endpoints have correct structure."""
    print("\nTesting endpoint structure...")
    
    try:
        from app.api.v1.endpoints import descriptive, inferential, qualitative, auto_detect
        
        # Check that routers exist
        assert hasattr(descriptive, 'router'), "Descriptive router missing"
        assert hasattr(inferential, 'router'), "Inferential router missing"  
        assert hasattr(qualitative, 'router'), "Qualitative router missing"
        assert hasattr(auto_detect, 'router'), "Auto-detect router missing"
        
        print("✓ All endpoint routers found")
        
        # Check that main API router can be imported
        from app.api.v1.api import api_router
        print("✓ Main API router imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Endpoint structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("ANALYTICS ENDPOINTS AUTO-DETECTION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_descriptive_auto_detection,
        test_inferential_auto_detection,
        test_qualitative_auto_detection,
        test_unified_auto_detector,
        test_endpoint_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! The analytics endpoints are ready to use.")
        print("\nEndpoint URLs (when server is running):")
        print("- Descriptive: /api/v1/descriptive/")
        print("- Inferential: /api/v1/inferential/")  
        print("- Qualitative: /api/v1/qualitative/")
        print("- Auto-detect: /api/v1/auto-detect/")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 