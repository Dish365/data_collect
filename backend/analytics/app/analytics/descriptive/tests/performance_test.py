"""
Performance testing for descriptive statistics functions.
"""

import time
import pandas as pd
import numpy as np
from app.analytics.descriptive import (
    calculate_basic_stats,
    get_outlier_summary,
    generate_full_report
)

def test_performance():
    """Test performance with different data sizes."""
    print("Performance Testing - Descriptive Statistics")
    print("="*50)
    
    sizes = [100, 1000, 10000, 50000]
    results = []
    
    for size in sizes:
        print(f"\nTesting with {size} rows...")
        
        # Generate data
        df = pd.DataFrame({
            'numeric1': np.random.normal(100, 15, size),
            'numeric2': np.random.exponential(10, size),
            'numeric3': np.random.lognormal(3, 0.5, size),
            'categorical1': np.random.choice(['A', 'B', 'C', 'D'], size),
            'categorical2': np.random.choice(['X', 'Y', 'Z'], size),
            'date': pd.date_range('2024-01-01', periods=size, freq='h')
        })
        
        # Add some missing values
        for col in df.select_dtypes(include=[np.number]).columns:
            missing_idx = np.random.choice(df.index, size=int(size*0.1), replace=False)
            df.loc[missing_idx, col] = np.nan
        
        # Test 1: Basic statistics
        start = time.time()
        basic_stats = calculate_basic_stats(df)
        basic_time = time.time() - start
        
        # Test 2: Outlier detection
        start = time.time()
        outliers = get_outlier_summary(df, methods=['iqr', 'zscore'])
        outlier_time = time.time() - start
        
        # Test 3: Full report (limited)
        start = time.time()
        report = generate_full_report(df.head(min(size, 1000)), include_advanced=False)
        report_time = time.time() - start
        
        results.append({
            'size': size,
            'basic_stats_time': basic_time,
            'outlier_time': outlier_time,
            'report_time': report_time
        })
        
        print(f"  Basic stats: {basic_time:.3f}s")
        print(f"  Outlier detection: {outlier_time:.3f}s")
        print(f"  Report generation: {report_time:.3f}s")
    
    # Summary
    print("\n" + "="*50)
    print("Performance Summary")
    print("="*50)
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    # Check scaling
    print("\nScaling Analysis:")
    for col in ['basic_stats_time', 'outlier_time']:
        times = results_df[col].values
        scaling = [times[i]/times[0] for i in range(len(times))]
        print(f"{col}: {scaling}")

if __name__ == "__main__":
    test_performance()