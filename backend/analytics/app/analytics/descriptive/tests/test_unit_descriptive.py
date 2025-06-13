"""
Unit tests for descriptive statistics functions.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.analytics.descriptive import (
    calculate_basic_stats,
    detect_outliers_iqr,
    analyze_categorical,
    calculate_chi_square
)

class TestBasicStatistics(unittest.TestCase):
    """Unit tests for basic statistics functions."""
    
    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.data = pd.DataFrame({
            'normal': np.random.normal(100, 15, 100),
            'skewed': np.random.lognormal(3, 0.5, 100),
            'categorical': np.random.choice(['A', 'B', 'C'], 100),
            'binary': np.random.choice([0, 1], 100)
        })
        
    def test_calculate_basic_stats(self):
        """Test basic statistics calculation."""
        stats = calculate_basic_stats(self.data, ['normal'])
        
        self.assertIn('normal', stats)
        self.assertIn('mean', stats['normal'])
        self.assertIn('std', stats['normal'])
        self.assertIn('skewness', stats['normal'])
        
        # Check approximate values
        self.assertAlmostEqual(stats['normal']['mean'], 100, delta=3)
        self.assertAlmostEqual(stats['normal']['std'], 15, delta=3)
        
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        stats = calculate_basic_stats(empty_df)
        self.assertEqual(stats, {})
        
    def test_all_missing_values(self):
        """Test handling of all missing values."""
        missing_df = pd.DataFrame({'col': [np.nan] * 10})
        stats = calculate_basic_stats(missing_df)
        self.assertEqual(stats['col']['count'], 0)
        self.assertEqual(stats['col']['missing_percentage'], 100.0)

class TestOutlierDetection(unittest.TestCase):
    """Unit tests for outlier detection."""
    
    def setUp(self):
        """Set up test data with known outliers."""
        self.data = pd.Series([1, 2, 3, 4, 5, 100])  # 100 is obvious outlier
        
    def test_iqr_outlier_detection(self):
        """Test IQR outlier detection."""
        result = detect_outliers_iqr(self.data)
        
        self.assertGreater(result['n_outliers'], 0)
        self.assertIn(100, result['outlier_values'])
        
    def test_zscore_outlier_detection(self):
        """Test Z-score outlier detection."""
        from app.analytics.descriptive import detect_outliers_zscore
        result = detect_outliers_zscore(self.data, threshold=2.0)
        
        self.assertGreater(result['n_outliers'], 0)
        self.assertIn(100, result['outlier_values'])

class TestCategoricalAnalysis(unittest.TestCase):
    """Unit tests for categorical analysis."""
    
    def setUp(self):
        """Set up test data."""
        self.data = pd.DataFrame({
            'category1': ['A', 'B', 'A', 'C', 'B', 'A'],
            'category2': ['X', 'Y', 'X', 'Y', 'X', 'Y']
        })
        
    def test_analyze_categorical(self):
        """Test categorical analysis."""
        result = analyze_categorical(self.data['category1'])
        
        self.assertEqual(result['unique_categories'], 3)
        self.assertEqual(result['mode'], 'A')
        self.assertIn('diversity', result)
        
    def test_chi_square(self):
        """Test chi-square test."""
        result = calculate_chi_square(self.data, 'category1', 'category2')
        
        self.assertIn('chi2_statistic', result)
        self.assertIn('p_value', result)
        self.assertIn('cramers_v', result)
        self.assertIsInstance(result['p_value'], float)

if __name__ == '__main__':
    unittest.main()