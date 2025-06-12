"""
Tests for analytics functionality.
"""

import pytest
import pandas as pd
import numpy as np
from ..analytics.descriptive.statistics import (
    calculate_basic_stats,
    calculate_correlation_matrix,
    calculate_frequency_distribution
)

@pytest.fixture
def sample_numeric_data():
    """Sample numeric data for testing."""
    return pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [2, 4, 6, 8, 10],
        'C': [1, 3, 5, 7, 9]
    })

@pytest.fixture
def sample_categorical_data():
    """Sample categorical data for testing."""
    return pd.DataFrame({
        'Category': ['A', 'B', 'A', 'C', 'B'],
        'Value': [1, 2, 3, 4, 5]
    })

def test_calculate_basic_stats(sample_numeric_data):
    """Test basic statistics calculation."""
    stats = calculate_basic_stats(sample_numeric_data)
    
    assert 'A' in stats
    assert 'mean' in stats['A']
    assert 'std' in stats['A']
    assert 'min' in stats['A']
    assert 'max' in stats['A']
    
    assert stats['A']['mean'] == 3.0
    assert stats['A']['min'] == 1.0
    assert stats['A']['max'] == 5.0

def test_calculate_correlation_matrix(sample_numeric_data):
    """Test correlation matrix calculation."""
    corr_matrix = calculate_correlation_matrix(sample_numeric_data)
    
    assert isinstance(corr_matrix, pd.DataFrame)
    assert corr_matrix.shape == (3, 3)
    assert corr_matrix.loc['A', 'B'] == pytest.approx(1.0)

def test_calculate_frequency_distribution(sample_categorical_data):
    """Test frequency distribution calculation."""
    freq_dist = calculate_frequency_distribution(sample_categorical_data, 'Category')
    
    assert freq_dist['A'] == 2
    assert freq_dist['B'] == 2
    assert freq_dist['C'] == 1 