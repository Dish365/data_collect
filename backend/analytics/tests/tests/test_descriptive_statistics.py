"""
Comprehensive test script for all descriptive statistics modules.
"""

import sys
import os
# Add the backend/analytics directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Import mock data generator
from mock_data_generator import generate_all_datasets

# Import all descriptive statistics modules
from app.analytics.descriptive import (
    # Basic statistics
    calculate_basic_stats,
    calculate_percentiles,
    calculate_grouped_stats,
    calculate_weighted_stats,
    calculate_correlation_matrix,
    
    # Distributions
    analyze_distribution,
    test_normality,
    calculate_skewness_kurtosis,
    fit_distribution,
    
    # Categorical analysis
    analyze_categorical,
    calculate_chi_square,
    calculate_cramers_v,
    analyze_cross_tabulation,
    
    # Outlier detection
    detect_outliers_iqr,
    detect_outliers_zscore,
    detect_outliers_isolation_forest,
    detect_outliers_mad,
    get_outlier_summary,
    
    # Missing data
    analyze_missing_data,
    get_missing_patterns,
    calculate_missing_correlations,
    
    # Temporal analysis
    analyze_temporal_patterns,
    calculate_time_series_stats,
    detect_seasonality,
    
    # Geospatial analysis
    analyze_spatial_distribution,
    calculate_spatial_autocorrelation,
    create_location_clusters,
    
    # Summary generation
    generate_full_report,
    generate_executive_summary,
    export_statistics
)

class TestDescriptiveStatistics:
    """Test class for descriptive statistics modules."""
    
    def __init__(self):
        self.datasets = generate_all_datasets()
        self.results = {}
        
    def test_basic_statistics(self):
        """Test basic statistics calculations."""
        print("\n" + "="*50)
        print("TESTING BASIC STATISTICS")
        print("="*50)
        
        df = self.datasets['commodity_production']
        
        # Test 1: Basic stats for all numeric columns
        print("\n1. Basic Statistics for All Numeric Columns:")
        basic_stats = calculate_basic_stats(df)
        
        for col, stats in list(basic_stats.items())[:3]:  # Show first 3
            print(f"\n{col}:")
            print(f"  Mean: {stats['mean']:.2f}")
            print(f"  Median: {stats['median']:.2f}")
            print(f"  Std Dev: {stats['std']:.2f}")
            print(f"  CV: {stats['cv']:.2f}" if stats['cv'] else "  CV: N/A")
            print(f"  Skewness: {stats['skewness']:.2f}")
            print(f"  Missing: {stats['missing_percentage']:.1f}%")
        
        # Test 2: Percentiles
        print("\n2. Percentile Analysis:")
        percentiles = calculate_percentiles(df, ['farm_size_hectares', 'yield_per_hectare_kg', 'price_per_kg_usd'])
        
        for col, percs in percentiles.items():
            print(f"\n{col} percentiles:")
            print(f"  P25: {percs['p25']:.2f}, P50: {percs['p50']:.2f}, P75: {percs['p75']:.2f}")
        
        # Test 3: Grouped statistics
        print("\n3. Grouped Statistics by Country:")
        grouped = calculate_grouped_stats(df, 'country', ['farm_size_hectares', 'yield_per_hectare_kg'])
        print(grouped.head(10))
        
        # Test 4: Weighted statistics (skip if no weight column)
        weighted = None
        if 'survey_weight' in df.columns:
            print("\n4. Weighted Statistics:")
            weighted = calculate_weighted_stats(df, 'yield_per_hectare_kg', 'survey_weight')
            print(f"  Weighted mean: {weighted['weighted_mean']:.2f}")
            print(f"  Weighted std: {weighted['weighted_std']:.2f}")
            print(f"  Effective sample size: {weighted['effective_sample_size']:.0f}")
        else:
            print("\n4. Weighted Statistics: Skipped (no weight column)")
        
        # Test 5: Correlation matrix
        print("\n5. Correlation Matrix:")
        numeric_cols = ['farm_size_hectares', 'yield_per_hectare_kg', 'price_per_kg_usd', 'total_production_kg']
        available_cols = [col for col in numeric_cols if col in df.columns]
        corr_matrix = calculate_correlation_matrix(df[available_cols])
        print(corr_matrix)
        
        self.results['basic_statistics'] = {
            'basic_stats': basic_stats,
            'percentiles': percentiles,
            'grouped_stats': grouped.to_dict(),
            'weighted_stats': weighted if weighted is not None else {},
            'correlations': corr_matrix.to_dict()
        }
        
    def test_distributions(self):
        """Test distribution analysis."""
        print("\n" + "="*50)
        print("TESTING DISTRIBUTION ANALYSIS")
        print("="*50)
        
        df = self.datasets['commodity_production']
        
        # Test 1: Distribution analysis
        print("\n1. Distribution Analysis for Key Variables:")
        
        for col in ['farm_size_hectares', 'yield_per_hectare_kg', 'price_per_kg_usd']:
            if col in df.columns:
                print(f"\n{col}:")
                dist_analysis = analyze_distribution(df[col])
                print(f"  Skewness: {dist_analysis['skewness']:.3f} ({dist_analysis['shape_interpretation']['skewness']})")
                print(f"  Kurtosis: {dist_analysis['excess_kurtosis']:.3f} ({dist_analysis['shape_interpretation']['kurtosis']})")
        
        # Test 2: Normality tests
        print("\n2. Normality Tests:")
        for col in ['yield_per_hectare_kg', 'price_per_kg_usd']:
            if col in df.columns:
                print(f"\n{col}:")
                norm_test = test_normality(df[col])
                print(f"  Shapiro-Wilk p-value: {norm_test.get('shapiro_wilk', {}).get('p_value', 'N/A'):.4f}")
                print(f"  Overall assessment: {norm_test['overall_assessment']['confidence']}")
        
        # Test 3: Distribution fitting
        print("\n3. Distribution Fitting for Production Revenue:")
        if 'gross_revenue_usd' in df.columns:
            revenue_data = df['gross_revenue_usd'].dropna()
            if len(revenue_data) > 10:
                fit_results = fit_distribution(revenue_data, ['norm', 'lognorm', 'gamma'])
                print(f"  Best fit: {fit_results['best_fit']['distribution']}")
                print(f"  AIC: {fit_results['best_fit']['aic']:.2f}")
        else:
            print("  Revenue data not available")
        
        self.results['distributions'] = {
            'distribution_analysis': {col: analyze_distribution(df[col]) 
                                    for col in ['farm_size_hectares', 'yield_per_hectare_kg', 'price_per_kg_usd'] if col in df.columns},
            'normality_tests': {col: test_normality(df[col]) 
                               for col in ['yield_per_hectare_kg', 'price_per_kg_usd'] if col in df.columns}
        }
        
    def test_categorical_analysis(self):
        """Test categorical data analysis."""
        print("\n" + "="*50)
        print("TESTING CATEGORICAL ANALYSIS")
        print("="*50)
        
        df = self.datasets['commodity_production']
        
        # Test 1: Categorical analysis
        print("\n1. Categorical Variable Analysis:")
        
        for col in ['country', 'commodity', 'certification_type']:
            if col in df.columns:
                print(f"\n{col}:")
                cat_analysis = analyze_categorical(df[col])
                print(f"  Unique categories: {cat_analysis['unique_categories']}")
                print(f"  Mode: {cat_analysis['mode']} ({cat_analysis['mode_percentage']:.1f}%)")
                print(f"  Shannon entropy: {cat_analysis['diversity']['shannon_entropy']:.3f}")
        
        # Test 2: Chi-square test
        print("\n2. Chi-Square Test (Country vs Commodity):")
        chi2_result = calculate_chi_square(df, 'country', 'commodity')
        print(f"  Chi-square statistic: {chi2_result['chi2_statistic']:.2f}")
        print(f"  P-value: {chi2_result['p_value']:.4f}")
        print(f"  Cramér's V: {chi2_result['cramers_v']:.3f}")
        print(f"  Interpretation: {chi2_result['effect_size_interpretation']}")
        
        # Test 3: Cross-tabulation
        print("\n3. Cross-tabulation (Country vs Has Certification):")
        if 'has_certification' in df.columns:
            crosstab = analyze_cross_tabulation(df, 'country', 'has_certification')
            print("Contingency Table:")
            print(pd.DataFrame(crosstab['crosstab']))
        else:
            print("  Certification data not available")
        
        self.results['categorical_analysis'] = {
            'categorical_stats': {col: analyze_categorical(df[col]) 
                                for col in ['country', 'commodity'] if col in df.columns},
            'chi_square': chi2_result,
            'crosstab': crosstab if 'has_certification' in df.columns else {}
        }
        
    def test_outlier_detection(self):
        """Test outlier detection methods."""
        print("\n" + "="*50)
        print("TESTING OUTLIER DETECTION")
        print("="*50)
        
        df = self.datasets['commodity_production']
        
        # Test different methods on yield (known to have outliers)
        print("\n1. Outlier Detection for Yield per Hectare:")
        
        # IQR method
        iqr_outliers = detect_outliers_iqr(df['yield_per_hectare_kg'])
        print(f"\nIQR Method:")
        print(f"  Outliers found: {iqr_outliers['n_outliers']}")
        print(f"  Percentage: {iqr_outliers['outlier_percentage']:.1f}%")
        print(f"  Bounds: [{iqr_outliers['lower_bound']:.1f}, {iqr_outliers['upper_bound']:.1f}]")
        
        # Z-score method
        zscore_outliers = detect_outliers_zscore(df['yield_per_hectare_kg'])
        print(f"\nZ-score Method:")
        print(f"  Outliers found: {zscore_outliers['n_outliers']}")
        print(f"  Percentage: {zscore_outliers['outlier_percentage']:.1f}%")
        
        # MAD method
        mad_outliers = detect_outliers_mad(df['yield_per_hectare_kg'])
        print(f"\nMAD Method:")
        print(f"  Outliers found: {mad_outliers['n_outliers']}")
        print(f"  Percentage: {mad_outliers['outlier_percentage']:.1f}%")
        
        # Test 2: Multivariate outlier detection
        print("\n2. Multivariate Outlier Detection:")
        numeric_cols = ['farm_size_hectares', 'yield_per_hectare_kg', 'price_per_kg_usd', 'total_production_kg']
        available_cols = [col for col in numeric_cols if col in df.columns]
        multi_outliers = detect_outliers_isolation_forest(df, columns=available_cols)
        print(f"  Outliers found: {multi_outliers['n_outliers']}")
        print(f"  Percentage: {multi_outliers['outlier_percentage']:.1f}%")
        
        # Test 3: Summary across all numeric columns
        print("\n3. Outlier Summary for All Numeric Columns:")
        outlier_summary = get_outlier_summary(df, methods=['iqr', 'zscore'])
        
        for col, results in list(outlier_summary.items())[:3]:
            consensus = results['consensus']
            print(f"\n{col}:")
            print(f"  Consensus outliers: {consensus['count']} ({consensus['percentage']:.1f}%)")
        
        self.results['outlier_detection'] = outlier_summary
        
    def test_missing_data_analysis(self):
        """Test missing data analysis."""
        print("\n" + "="*50)
        print("TESTING MISSING DATA ANALYSIS")
        print("="*50)
        
        df = self.datasets['commodity_production']
        
        # Test 1: Overall missing data analysis
        print("\n1. Missing Data Summary:")
        missing_analysis = analyze_missing_data(df)
        summary = missing_analysis['summary']
        
        print(f"  Total missing cells: {summary['total_missing']} ({summary['total_missing_percentage']:.1f}%)")
        print(f"  Columns with missing: {summary['columns_with_missing']}")
        print(f"  Complete rows: {summary['complete_rows']} ({summary['complete_rows_percentage']:.1f}%)")
        
        # Test 2: Missing patterns
        print("\n2. Missing Data Patterns:")
        patterns = missing_analysis['patterns']
        print(f"  Unique patterns: {patterns['unique_patterns']}")
        
        if patterns['top_patterns']:
            print("\n  Most common pattern:")
            pattern1 = patterns['top_patterns']['pattern_1']
            print(f"    Missing columns: {pattern1['missing_columns']}")
            print(f"    Count: {pattern1['count']} ({pattern1['percentage']:.1f}%)")
        
        # Test 3: Missing correlations
        print("\n3. Missing Data Correlations:")
        missing_corr = calculate_missing_correlations(df)
        if not missing_corr.empty:
            print("Correlation between missing indicators:")
            print(missing_corr.iloc[:3, :3])  # Show subset
        
        self.results['missing_data'] = missing_analysis
        
    def test_temporal_analysis(self):
        """Test temporal analysis."""
        print("\n" + "="*50)
        print("TESTING TEMPORAL ANALYSIS")
        print("="*50)
        
        df = self.datasets['commodity_production']
        
        # Test 1: Temporal patterns
        print("\n1. Temporal Patterns Analysis:")
        temporal = analyze_temporal_patterns(
            df, 
            'collection_date',
            ['yield_per_hectare_kg', 'price_per_kg_usd']
        )
        
        date_range = temporal['date_range']
        print(f"  Date range: {date_range['start']} to {date_range['end']}")
        print(f"  Duration: {date_range['duration_days']} days")
        print(f"  Coverage: {date_range['date_coverage']['coverage_percentage']:.1f}%")
        
        # Response patterns
        patterns = temporal['response_patterns']
        print(f"\n  Busiest day: {patterns['busiest_day']}")
        print(f"  Weekend percentage: {patterns['weekend_percentage']:.1f}%")
        
        # Test 2: Time series statistics
        print("\n2. Time Series Statistics:")
        # Create a time series
        ts_data = df.groupby('collection_date')['yield_per_hectare_kg'].mean()
        if len(ts_data) > 20:
            ts_stats = calculate_time_series_stats(ts_data, ts_data.index)
            print(f"  Length: {ts_stats['length']}")
            if 'adf_test' in ts_stats:
                print(f"  ADF test p-value: {ts_stats['adf_test']['p_value']:.4f}")
                print(f"  Is stationary: {ts_stats['adf_test']['is_stationary']}")
        
        self.results['temporal_analysis'] = temporal
        
    def test_geospatial_analysis(self):
        """Test geospatial analysis."""
        print("\n" + "="*50)
        print("TESTING GEOSPATIAL ANALYSIS")
        print("="*50)
        
        df = self.datasets['commodity_production']
        
        # Test 1: Spatial distribution
        print("\n1. Spatial Distribution Analysis:")
        spatial = analyze_spatial_distribution(
            df, 
            'latitude', 
            'longitude',
            'yield_per_hectare_kg'
        )
        
        bbox = spatial['bounding_box']
        print(f"  Total points: {spatial['total_points']}")
        print(f"  Bounding box: ({bbox['min_lat']:.4f}, {bbox['min_lon']:.4f}) to ({bbox['max_lat']:.4f}, {bbox['max_lon']:.4f})")
        print(f"  Mean distance between points: {spatial['distance_stats']['mean_distance_km']:.2f} km")
        
        if 'clusters' in spatial:
            clusters = spatial['clusters']
            print(f"\n  Spatial clusters found: {clusters['n_clusters']}")
            print(f"  Noise points: {clusters['n_noise_points']}")
        
        # Test 2: Spatial autocorrelation
        print("\n2. Spatial Autocorrelation (Yield per Hectare):")
        spatial_auto = calculate_spatial_autocorrelation(
            df.dropna(subset=['latitude', 'longitude', 'yield_per_hectare_kg']),
            'latitude',
            'longitude', 
            'yield_per_hectare_kg',
            max_distance_km=50
        )
        
        if 'error' not in spatial_auto:
            print(f"  Moran's I: {spatial_auto['morans_i']:.4f}")
            print(f"  Expected I: {spatial_auto['expected_i']:.4f}")
            print(f"  Interpretation: {spatial_auto['interpretation']}")
        
        # Test 3: Location clustering
        print("\n3. Creating Location Clusters:")
        df_clustered = create_location_clusters(df, 'latitude', 'longitude', n_clusters=6)
        cluster_counts = df_clustered['location_cluster'].value_counts()
        print(f"  Cluster distribution: {cluster_counts.to_dict()}")
        
        self.results['geospatial_analysis'] = spatial
        
    def test_summary_generation(self):
        """Test summary generation and reporting."""
        print("\n" + "="*50)
        print("TESTING SUMMARY GENERATION")
        print("="*50)
        
        df = self.datasets['trade_flows']
        
        # Test 1: Executive summary
        print("\n1. Executive Summary:")
        exec_summary = generate_executive_summary(df)
        
        overview = exec_summary['overview']
        print(f"  Total observations: {overview['total_observations']}")
        print(f"  Variables: {overview['total_variables']} ({overview['numeric_variables']} numeric, {overview['categorical_variables']} categorical)")
        print(f"  Memory usage: {overview['memory_usage_mb']:.2f} MB")
        
        print("\n  Key Insights:")
        for insight in exec_summary['key_insights'][:3]:
            print(f"    - {insight}")
        
        print("\n  Recommendations:")
        for rec in exec_summary['recommendations'][:3]:
            print(f"    - {rec}")
        
        # Test 2: Full report (limited scope for testing)
        print("\n2. Generating Full Report...")
        full_report = generate_full_report(
            df.iloc[:100],  # Use subset for speed
            project_name="Commodity Trade Study Test",
            include_advanced=False
        )
        
        print(f"  Report sections: {list(full_report.keys())}")
        print(f"  Data quality complete: {full_report['data_quality']['missing_data']['summary']['complete_rows_percentage']:.1f}%")
        
        # Test 3: Export formats
        print("\n3. Testing Export Formats:")
        
        # JSON export
        json_export = export_statistics(exec_summary, format='json')
        print(f"  JSON export length: {len(json_export)} characters")
        
        # Markdown export
        md_export = export_statistics(full_report, format='markdown')
        print(f"  Markdown export length: {len(md_export)} characters")
        print("\n  First few lines of Markdown:")
        print('\n'.join(md_export.split('\n')[:5]))
        
        self.results['summary_generation'] = {
            'executive_summary': exec_summary,
            'full_report_sections': list(full_report.keys())
        }
        
    def run_all_tests(self):
        """Run all tests and save results."""
        print("\n" + "="*70)
        print("COMPREHENSIVE DESCRIPTIVE STATISTICS TEST SUITE")
        print("="*70)
        
        # Run all test methods
        test_methods = [
            self.test_basic_statistics,
            self.test_distributions,
            self.test_categorical_analysis,
            self.test_outlier_detection,
            self.test_missing_data_analysis,
            self.test_temporal_analysis,
            self.test_geospatial_analysis,
            self.test_summary_generation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"\nERROR in {test_method.__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Save results
        self.save_results()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED")
        print("="*70)
        
    def save_results(self):
        """Save test results to file."""
        results_file = 'test_results_descriptive_statistics.json'
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict()
            elif isinstance(obj, dict):
                # Handle tuple keys and numpy integer keys by converting them to appropriate types
                converted_dict = {}
                for k, v in obj.items():
                    if isinstance(k, tuple):
                        # Convert tuple key to string representation
                        key_str = str(k)
                    elif isinstance(k, np.integer):
                        # Convert numpy integer key to regular Python int
                        key_str = int(k)
                    elif isinstance(k, np.floating):
                        # Convert numpy float key to regular Python float
                        key_str = float(k)
                    else:
                        key_str = k
                    converted_dict[key_str] = convert_types(v)
                return converted_dict
            elif isinstance(obj, list):
                return [convert_types(v) for v in obj]
            else:
                return obj
        
        # Save results
        results_to_save = convert_types(self.results)
        
        with open(results_file, 'w') as f:
            json.dump(results_to_save, f, indent=2, default=str)
        
        print(f"\nResults saved to {results_file}")
        
if __name__ == "__main__":
    # Run all tests
    tester = TestDescriptiveStatistics()
    tester.run_all_tests()