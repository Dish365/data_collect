"""
Quick test runner for specific descriptive statistics functions.
"""

import pandas as pd
import numpy as np
from mock_data_generator import generate_rural_health_survey_data

# Import specific functions to test
from app.analytics.descriptive import (
    calculate_basic_stats,
    detect_outliers_iqr,
    analyze_missing_data,
    generate_executive_summary
)

def quick_test():
    """Run quick tests on key functions."""
    print("Generating test data...")
    df = generate_rural_health_survey_data(100)  # Small dataset for quick testing
    
    print("\n1. Basic Statistics Test:")
    stats = calculate_basic_stats(df, columns=['age', 'bmi', 'health_score'])
    for col, col_stats in stats.items():
        print(f"\n{col}:")
        print(f"  Mean: {col_stats['mean']:.2f}")
        print(f"  Std: {col_stats['std']:.2f}")
        print(f"  Missing: {col_stats['missing_percentage']:.1f}%")
    
    print("\n2. Outlier Detection Test:")
    outliers = detect_outliers_iqr(df['bmi'])
    print(f"  Found {outliers['n_outliers']} outliers ({outliers['outlier_percentage']:.1f}%)")
    
    print("\n3. Missing Data Test:")
    missing = analyze_missing_data(df)
    summary = missing['summary']
    print(f"  Total missing: {summary['total_missing_percentage']:.1f}%")
    print(f"  Complete rows: {summary['complete_rows_percentage']:.1f}%")
    
    print("\n4. Executive Summary Test:")
    summary = generate_executive_summary(df)
    print(f"  Dataset has {summary['overview']['total_observations']} observations")
    print(f"  Key insights: {summary['key_insights'][0]}")

if __name__ == "__main__":
    quick_test()