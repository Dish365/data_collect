"""
Auto-detection module for data type and analysis detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def detect_data_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect data types of columns.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary mapping column names to detected types
    """
    type_mapping = {}
    
    for column in df.columns:
        # Check if column is numeric
        if pd.api.types.is_numeric_dtype(df[column]):
            # Check if it's a binary/categorical numeric
            unique_ratio = df[column].nunique() / len(df)
            if unique_ratio < 0.05:  # Less than 5% unique values
                type_mapping[column] = "categorical"
            else:
                type_mapping[column] = "numeric"
        
        # Check if column is datetime
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            type_mapping[column] = "datetime"
        
        # Check if column is text
        elif pd.api.types.is_string_dtype(df[column]):
            # Check if it's categorical text
            unique_ratio = df[column].nunique() / len(df)
            if unique_ratio < 0.05:  # Less than 5% unique values
                type_mapping[column] = "categorical"
            else:
                type_mapping[column] = "text"
        
        else:
            type_mapping[column] = "unknown"
    
    return type_mapping

def detect_distribution(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Detect the distribution of a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column to analyze
        
    Returns:
        Dictionary with distribution information
    """
    data = df[column].dropna()
    
    # Calculate basic statistics
    mean = data.mean()
    std = data.std()
    skew = data.skew()
    kurtosis = data.kurtosis()
    
    # Perform normality test
    _, p_value = stats.normaltest(data)
    
    # Determine distribution type
    if p_value > 0.05:
        distribution = "normal"
    elif abs(skew) > 1:
        distribution = "skewed"
    elif abs(kurtosis) > 3:
        distribution = "heavy-tailed"
    else:
        distribution = "unknown"
    
    return {
        "distribution": distribution,
        "mean": float(mean),
        "std": float(std),
        "skew": float(skew),
        "kurtosis": float(kurtosis),
        "normality_test_p_value": float(p_value)
    }

def detect_correlations(
    df: pd.DataFrame,
    threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Detect significant correlations between numeric columns.
    
    Args:
        df: Input DataFrame
        threshold: Correlation threshold
        
    Returns:
        List of significant correlations
    """
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()
    
    correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr = corr_matrix.iloc[i, j]
            if abs(corr) >= threshold:
                correlations.append({
                    "column1": corr_matrix.columns[i],
                    "column2": corr_matrix.columns[j],
                    "correlation": float(corr)
                })
    
    return correlations

def detect_clusters(
    df: pd.DataFrame,
    max_clusters: int = 5
) -> Dict[str, Any]:
    """
    Detect natural clusters in numeric data.
    
    Args:
        df: Input DataFrame
        max_clusters: Maximum number of clusters to try
        
    Returns:
        Dictionary with clustering information
    """
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_df)
    
    # Reduce dimensionality if needed
    if scaled_data.shape[1] > 2:
        pca = PCA(n_components=2)
        scaled_data = pca.fit_transform(scaled_data)
    
    # Try different numbers of clusters
    best_n_clusters = 1
    best_score = float('-inf')
    
    for n_clusters in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(scaled_data)
        score = -kmeans.inertia_  # Negative inertia as score
        
        if score > best_score:
            best_score = score
            best_n_clusters = n_clusters
    
    # Fit final model
    final_kmeans = KMeans(n_clusters=best_n_clusters, random_state=42)
    clusters = final_kmeans.fit_predict(scaled_data)
    
    return {
        "n_clusters": best_n_clusters,
        "cluster_sizes": pd.Series(clusters).value_counts().to_dict(),
        "cluster_centers": final_kmeans.cluster_centers_.tolist()
    }

def suggest_analyses(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Suggest appropriate analyses based on data characteristics.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with suggested analyses
    """
    suggestions = {
        "descriptive": [],
        "inferential": [],
        "qualitative": []
    }
    
    # Detect data types
    data_types = detect_data_types(df)
    
    # Check for numeric columns
    numeric_cols = [col for col, type_ in data_types.items() if type_ == "numeric"]
    if numeric_cols:
        suggestions["descriptive"].extend([
            "basic_statistics",
            "correlation_analysis",
            "distribution_analysis"
        ])
        
        if len(numeric_cols) >= 2:
            suggestions["inferential"].extend([
                "correlation_tests",
                "regression_analysis"
            ])
    
    # Check for categorical columns
    categorical_cols = [col for col, type_ in data_types.items() if type_ == "categorical"]
    if categorical_cols:
        suggestions["descriptive"].extend([
            "frequency_analysis",
            "cross_tabulation"
        ])
        
        if len(categorical_cols) >= 2:
            suggestions["inferential"].extend([
                "chi_square_tests",
                "contingency_analysis"
            ])
    
    # Check for text columns
    text_cols = [col for col, type_ in data_types.items() if type_ == "text"]
    if text_cols:
        suggestions["qualitative"].extend([
            "text_analysis",
            "sentiment_analysis",
            "topic_modeling"
        ])
    
    # Check for datetime columns
    datetime_cols = [col for col, type_ in data_types.items() if type_ == "datetime"]
    if datetime_cols:
        suggestions["descriptive"].extend([
            "time_series_analysis",
            "trend_analysis"
        ])
    
    return suggestions 