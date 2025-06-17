"""
Integration test combining data generation, analysis, and visualization.
"""

import time
from mock_data_generator import generate_all_datasets
from test_descriptive_statistics import TestDescriptiveStatistics
from visualize_results import DescriptiveStatsVisualizer

def run_integration_test():
    """Run complete integration test."""
    print("="*70)
    print("DESCRIPTIVE STATISTICS INTEGRATION TEST")
    print("="*70)
    
    start_time = time.time()
    
    # Step 1: Generate data
    print("\n1. Generating mock datasets...")
    datasets = generate_all_datasets()
    print(f"✓ Generated {len(datasets)} datasets")
    
    # Step 2: Run statistical tests
    print("\n2. Running statistical analyses...")
    tester = TestDescriptiveStatistics()
    tester.run_all_tests()
    print("✓ Statistical analyses completed")
    
    # Step 3: Create visualizations
    print("\n3. Creating visualizations...")
    visualizer = DescriptiveStatsVisualizer()
    visualizer.run_all_visualizations()
    print("✓ Visualizations created")
    
    # Summary
    elapsed_time = time.time() - start_time
    print("\n" + "="*70)
    print("INTEGRATION TEST COMPLETED")
    print(f"Total time: {elapsed_time:.2f} seconds")
    print("="*70)
    
    print("\nGenerated files:")
    print("- mock_rural_health_data.csv")
    print("- mock_education_data.csv") 
    print("- mock_agriculture_data.csv")
    print("- test_results_descriptive_statistics.json")
    print("- basic_statistics_visualization.png")
    print("- distribution_analysis.png")
    print("- categorical_analysis.png")
    print("- outlier_analysis.png")
    print("- temporal_analysis.png")
    print("- geospatial_analysis.png")
    print("- comprehensive_dashboard.png")

if __name__ == "__main__":
    run_integration_test()