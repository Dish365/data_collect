"""
Descriptive statistics module for comprehensive data analysis.
"""

from .basic_statistics import (
    calculate_basic_stats,
    calculate_percentiles,
    calculate_grouped_stats,
    calculate_weighted_stats,
    calculate_correlation_matrix,
    calculate_covariance_matrix
)

from .distributions import (
    analyze_distribution,
    test_normality,
    calculate_skewness_kurtosis,
    fit_distribution
)

from .categorical_analysis import (
    analyze_categorical,
    calculate_chi_square,
    calculate_cramers_v,
    analyze_cross_tabulation
)

from .outlier_detection import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    detect_outliers_isolation_forest,
    detect_outliers_mad,
    get_outlier_summary
)

from .missing_data import (
    analyze_missing_data,
    get_missing_patterns,
    calculate_missing_correlations
)

from .temporal_analysis import (
    analyze_temporal_patterns,
    calculate_time_series_stats,
    detect_seasonality
)

from .geospatial_analysis import (
    analyze_spatial_distribution,
    calculate_spatial_autocorrelation,
    create_location_clusters
)

from .summary_generator import (
    generate_full_report,
    generate_executive_summary,
    export_statistics
)

__all__ = [
    'calculate_basic_stats',
    'calculate_percentiles',
    'calculate_grouped_stats',
    'calculate_weighted_stats',
    'calculate_correlation_matrix',
    'calculate_covariance_matrix',
    'analyze_distribution',
    'test_normality',
    'calculate_skewness_kurtosis',
    'fit_distribution',
    'analyze_categorical',
    'calculate_chi_square',
    'calculate_cramers_v',
    'analyze_cross_tabulation',
    'detect_outliers_iqr',
    'detect_outliers_zscore',
    'detect_outliers_isolation_forest',
    'detect_outliers_mad',
    'get_outlier_summary',
    'analyze_missing_data',
    'get_missing_patterns',
    'calculate_missing_correlations',
    'analyze_temporal_patterns',
    'calculate_time_series_stats',
    'detect_seasonality',
    'analyze_spatial_distribution',
    'calculate_spatial_autocorrelation',
    'create_location_clusters',
    'generate_full_report',
    'generate_executive_summary',
    'export_statistics'
]