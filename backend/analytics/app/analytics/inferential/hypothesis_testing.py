"""
Hypothesis testing module for inferential analytics.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple

def perform_t_test(
    data1: pd.Series,
    data2: pd.Series,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Perform a t-test between two samples.
    
    Args:
        data1: First sample
        data2: Second sample
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    t_stat, p_value = stats.ttest_ind(data1, data2)
    
    return {
        "test_type": "t-test",
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": p_value < alpha,
        "alpha": alpha
    }

def perform_anova(
    data: pd.DataFrame,
    group_column: str,
    value_column: str,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Perform one-way ANOVA test.
    
    Args:
        data: DataFrame containing the data
        group_column: Column containing group labels
        value_column: Column containing values to test
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    groups = [group for _, group in data.groupby(group_column)[value_column]]
    f_stat, p_value = stats.f_oneway(*groups)
    
    return {
        "test_type": "one-way ANOVA",
        "f_statistic": float(f_stat),
        "p_value": float(p_value),
        "significant": p_value < alpha,
        "alpha": alpha
    }

def perform_chi_square_test(
    observed: pd.DataFrame,
    expected: pd.DataFrame = None,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Perform chi-square test of independence.
    
    Args:
        observed: Observed frequencies
        expected: Expected frequencies (optional)
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    if expected is None:
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
    else:
        chi2, p_value, dof, _ = stats.chi2_contingency(observed, expected)
    
    return {
        "test_type": "chi-square",
        "chi2_statistic": float(chi2),
        "p_value": float(p_value),
        "degrees_of_freedom": int(dof),
        "significant": p_value < alpha,
        "alpha": alpha,
        "expected_frequencies": expected.tolist()
    }

def perform_correlation_test(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    method: str = "pearson",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Perform correlation test between two variables.
    
    Args:
        data: DataFrame containing the data
        x_column: First variable column
        y_column: Second variable column
        method: Correlation method ('pearson', 'spearman', or 'kendall')
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    if method == "pearson":
        corr, p_value = stats.pearsonr(data[x_column], data[y_column])
    elif method == "spearman":
        corr, p_value = stats.spearmanr(data[x_column], data[y_column])
    elif method == "kendall":
        corr, p_value = stats.kendalltau(data[x_column], data[y_column])
    else:
        raise ValueError(f"Unsupported correlation method: {method}")
    
    return {
        "test_type": f"{method} correlation",
        "correlation": float(corr),
        "p_value": float(p_value),
        "significant": p_value < alpha,
        "alpha": alpha
    } 