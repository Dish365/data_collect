"""
Test script to verify Django database connectivity from analytics backend.
Run this to test database paths and connections before starting the server.
"""

import sys
import os
from pathlib import Path

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_database_connection():
    """Test Django database connection"""
    print("Testing Django database connection...")
    
    try:
        from app.utils.shared import AnalyticsUtils
        
        # Test connection
        conn = AnalyticsUtils.get_django_db_connection()
        print("✅ Successfully connected to Django database")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ Found {len(tables)} tables in database:")
        for table in tables[:10]:  # Show first 10 tables
            print(f"   - {table[0]}")
        
        if len(tables) > 10:
            print(f"   ... and {len(tables) - 10} more tables")
        
        # Test project-related tables
        django_tables = ['projects_project', 'forms_question', 'responses_response']
        missing_tables = []
        
        table_names = [table[0] for table in tables]
        for table in django_tables:
            if table in table_names:
                print(f"✅ Found expected table: {table}")
            else:
                missing_tables.append(table)
                print(f"⚠️  Missing expected table: {table}")
        
        if missing_tables:
            print(f"\n⚠️  Warning: Missing {len(missing_tables)} expected Django tables")
            print("   This might indicate the Django database is not fully set up")
        else:
            print("\n✅ All expected Django tables found!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_sample_data():
    """Test sample data retrieval"""
    print("\nTesting sample data retrieval...")
    
    try:
        from app.utils.shared import AnalyticsUtils
        
        # Try to get a sample project's data
        test_project_id = "test_project_123"
        df = AnalyticsUtils.get_project_data(test_project_id)
        
        if df.empty:
            print(f"ℹ️  No data found for project '{test_project_id}' (this is expected for test)")
        else:
            print(f"✅ Found data: {len(df)} rows, {len(df.columns)} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Data retrieval test failed: {e}")
        return False

def test_analytics_functions():
    """Test analytics utility functions"""
    print("\nTesting analytics utility functions...")
    
    try:
        from app.utils.shared import AnalyticsUtils
        import pandas as pd
        import numpy as np
        
        # Create sample data
        np.random.seed(42)
        sample_data = pd.DataFrame({
            'numeric_var': np.random.normal(100, 15, 20),
            'category': np.random.choice(['A', 'B', 'C'], 20),
            'text_data': [f"Sample text {i}" for i in range(20)]
        })
        
        # Test data characteristics
        characteristics = AnalyticsUtils.analyze_data_characteristics(sample_data)
        print(f"✅ Data characteristics: {characteristics['sample_size']} samples, {characteristics['variable_count']} variables")
        
        # Test recommendations
        recommendations = AnalyticsUtils.generate_analysis_recommendations(characteristics)
        print(f"✅ Generated {len(recommendations)} analysis recommendations")
        
        # Test descriptive analysis
        results = AnalyticsUtils.run_descriptive_analysis(sample_data)
        print(f"✅ Descriptive analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics functions test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Django Database Connectivity Test")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Sample Data Retrieval", test_sample_data),
        ("Analytics Functions", test_analytics_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
    
    print(f"\n{'=' * 50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database connectivity is working correctly.")
        print("\n🚀 Ready to start analytics backend:")
        print("   python start_analytics.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Common issues:")
        print("   - Django database not found: Run Django migrations first")
        print("   - Path issues: Check file paths in AnalyticsUtils")
        print("   - Missing tables: Set up Django models and migrate")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 