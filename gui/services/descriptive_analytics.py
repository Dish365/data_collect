"""
Descriptive Analytics Handler
Specialized service for descriptive statistics and data analysis
"""

from typing import Dict, List, Any, Optional
import threading
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class DescriptiveAnalyticsHandler:
    """Handler for descriptive analytics operations - Business Logic Only"""
    
    def __init__(self, analytics_service, analytics_screen):
        self.analytics_service = analytics_service
        self.analytics_screen = analytics_screen
        self.selected_variables = []
    
    def run_descriptive_analysis(self, project_id: str, analysis_config: Dict = None):
        """Run descriptive analysis for the project"""
        if not project_id:
            return
            
        self.analytics_screen.set_loading(True)
        threading.Thread(
            target=self._run_descriptive_thread,
            args=(project_id, analysis_config),
            daemon=True
        ).start()
    
    def _run_descriptive_thread(self, project_id: str, analysis_config: Dict):
        """Background thread for descriptive analysis"""
        try:
            # Run comprehensive descriptive analysis
            results = self.analytics_service.run_descriptive_analysis(project_id, analysis_config)
            
            Clock.schedule_once(
                lambda dt: self._handle_descriptive_results(results), 0
            )
        except Exception as e:
            print(f"Error in descriptive analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Descriptive analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _handle_descriptive_results(self, results):
        """Handle descriptive analysis results - delegate to UI"""
        print(f"[DEBUG] Descriptive results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                toast("Backend connection error")
            else:
                toast(f"Analysis Error: {error_msg}")
            return
        
        # Delegate to analytics screen to handle UI display
        self.analytics_screen.display_descriptive_results(results)
    
    def get_analysis_options(self, project_id: str) -> List[Dict]:
        """Get available analysis options for descriptive analytics"""
        return [
            {
                'name': 'Basic Statistics',
                'description': 'Calculate mean, median, standard deviation, and other basic statistics for numeric variables.',
                'suitable_for': 'Numeric variables with continuous or discrete data',
                'icon': '📊',
                'endpoint': 'basic-statistics',
                'color': (0.2, 0.6, 1.0, 1)
            },
            {
                'name': 'Distribution Analysis',
                'description': 'Analyze data distributions, identify patterns, and detect skewness or unusual distributions.',
                'suitable_for': 'Numeric variables to understand data shape and patterns',
                'icon': '📈',
                'endpoint': 'distributions',
                'color': (0.8, 0.6, 0.2, 1)
            },
            {
                'name': 'Categorical Analysis',
                'description': 'Analyze categorical variables with frequency tables, chi-square tests, and cross-tabulations.',
                'suitable_for': 'Categorical variables with discrete categories',
                'icon': '📋',
                'endpoint': 'categorical',
                'color': (0.2, 0.8, 0.6, 1)
            },
            {
                'name': 'Outlier Detection',
                'description': 'Identify and analyze outliers using statistical methods and visualization.',
                'suitable_for': 'Numeric variables to find unusual data points',
                'icon': '🎯',
                'endpoint': 'outliers',
                'color': (0.8, 0.2, 0.2, 1)
            },
            {
                'name': 'Missing Data Analysis',
                'description': 'Analyze patterns of missing data and assess data completeness.',
                'suitable_for': 'All variables to understand data quality',
                'icon': '❓',
                'endpoint': 'missing-data',
                'color': (0.6, 0.6, 0.6, 1)
            },
            {
                'name': 'Data Quality Assessment',
                'description': 'Comprehensive data quality analysis including completeness, consistency, and validity.',
                'suitable_for': 'All variables for quality assessment',
                'icon': '✅',
                'endpoint': 'data-quality',
                'color': (0.2, 0.8, 0.4, 1)
            }
        ]
    
    def get_sample_size_recommendations(self, project_id: str) -> List[Dict]:
        """Get sample size recommendations for statistical tests"""
        try:
            # Get project variables to determine appropriate tests
            variables = self.analytics_service.get_project_variables(project_id)
            
            if not variables or 'error' in variables:
                return []
            
            recommendations = []
            
            # Basic statistics recommendations
            if variables.get('numeric', []):
                recommendations.append({
                    'test_type': 'Basic Statistics',
                    'current_size': len(variables['numeric']),
                    'adequacy': 'adequate',
                    'recommendation': 'Sufficient sample size for basic statistical analysis',
                    'needed_for_medium_effect': 30
                })
            
            # Chi-square test recommendations
            if variables.get('categorical', []):
                recommendations.append({
                    'test_type': 'Chi-Square Test',
                    'current_size': len(variables['categorical']),
                    'adequacy': 'adequate',
                    'recommendation': 'Adequate sample size for chi-square analysis',
                    'minimum_needed': 20
                })
            
            # Correlation analysis recommendations
            if len(variables.get('numeric', [])) > 1:
                recommendations.append({
                    'test_type': 'Correlation Analysis',
                    'current_size': len(variables['numeric']),
                    'adequacy': 'adequate',
                    'recommendation': 'Sufficient variables for correlation analysis',
                    'minimum_needed': 2
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting sample size recommendations: {e}")
            return []
    
    def get_comprehensive_report_data(self, report_data: Dict) -> Dict:
        """Extract comprehensive report data for UI consumption"""
        if 'error' in report_data:
            return {
                'has_error': True,
                'error_message': report_data['error']
            }
        
        metadata = report_data.get('report_metadata', {})
        executive_summary = report_data.get('executive_summary', {})
        
        return {
            'has_error': False,
            'report_type': metadata.get('report_type', 'Comprehensive Analysis'),
            'generated_at': metadata.get('generated_at', 'N/A'),
            'data_shape': metadata.get('data_shape', 'N/A'),
            'variables_analyzed': metadata.get('variables_analyzed', 'N/A'),
            'executive_summary': executive_summary.get('overview', 'No summary available') if isinstance(executive_summary, dict) else str(executive_summary)
        }
    
    def get_data_quality_data(self, quality_data: Dict) -> Dict:
        """Extract data quality analysis data for UI consumption"""
        if 'error' in quality_data:
            return {
                'has_error': True,
                'error_message': quality_data['error']
            }
        
        return {
            'has_error': False,
            'overall_score': quality_data.get('overall_score', 0),
            'completeness_score': quality_data.get('completeness_score', 0),
            'consistency_score': quality_data.get('consistency_score', 0),
            'validity_score': quality_data.get('validity_score', 0),
            'quality_details': quality_data.get('quality_details', {}),
            'recommendations': quality_data.get('recommendations', [])
        }
    
    def get_basic_statistics_data(self, stats_data: Dict) -> Dict:
        """Extract basic statistics data for UI consumption"""
        if 'error' in stats_data:
            return {
                'has_error': True,
                'error_message': stats_data['error']
            }
        
        return {
            'has_error': False,
            'summary_stats': stats_data.get('summary_statistics', {}),
            'variable_stats': stats_data.get('variable_statistics', {}),
            'total_variables': stats_data.get('total_variables', 0),
            'total_observations': stats_data.get('total_observations', 0)
        }
    
    def get_variable_statistics_data(self, var_name: str, var_stats: Dict) -> Dict:
        """Extract variable statistics data for UI consumption"""
        return {
            'variable_name': var_name,
            'count': var_stats.get('count', 0),
            'mean': var_stats.get('mean', 'N/A'),
            'std': var_stats.get('std', 'N/A'),
            'min': var_stats.get('min', 'N/A'),
            'max': var_stats.get('max', 'N/A'),
            'median': var_stats.get('median', 'N/A'),
            'missing': var_stats.get('missing', 0)
        }
    
    def run_specific_analysis(self, project_id: str, endpoint: str, analysis_name: str):
        """Run a specific descriptive analysis"""
        print(f"[DEBUG] Running {analysis_name} analysis for project {project_id}")
        toast(f"Running {analysis_name}...")
        
        self.analytics_screen.set_loading(True)
        threading.Thread(
            target=self._specific_analysis_thread,
            args=(project_id, endpoint, analysis_name),
            daemon=True
        ).start()
    
    def _specific_analysis_thread(self, project_id: str, endpoint: str, analysis_name: str):
        """Background thread for specific analysis"""
        try:
            # Call the appropriate analytics service method
            if endpoint == 'basic-statistics':
                results = self.analytics_service.run_basic_statistics(project_id)
            elif endpoint == 'distributions':
                results = self.analytics_service.run_distribution_analysis(project_id)
            elif endpoint == 'categorical':
                results = self.analytics_service.run_categorical_analysis(project_id)
            elif endpoint == 'outliers':
                results = self.analytics_service.run_outlier_analysis(project_id)
            elif endpoint == 'missing-data':
                results = self.analytics_service.run_missing_data_analysis(project_id)
            elif endpoint == 'data-quality':
                results = self.analytics_service.run_data_quality_analysis(project_id)
            else:
                results = {'error': f'Unknown analysis endpoint: {endpoint}'}
            
            Clock.schedule_once(
                lambda dt: self._handle_specific_analysis_results(results, analysis_name), 0
            )
        except Exception as e:
            print(f"Error in specific analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast(f"{analysis_name} analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _handle_specific_analysis_results(self, results: Dict, analysis_name: str):
        """Handle specific analysis results - delegate to UI"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"{analysis_name} Error: {error_msg}")
            return
        
        # Delegate to analytics screen to handle UI display
        self.analytics_screen.display_specific_analysis_results(results, analysis_name)
    
    def run_comprehensive_report(self, project_id: str):
        """Run comprehensive descriptive report"""
        print(f"[DEBUG] Running comprehensive report for project {project_id}")
        toast("Generating comprehensive report...")
        
        self.analytics_screen.set_loading(True)
        threading.Thread(
            target=self._comprehensive_report_thread,
            args=(project_id,),
            daemon=True
        ).start()
    
    def _comprehensive_report_thread(self, project_id: str):
        """Background thread for comprehensive report"""
        try:
            results = self.analytics_service.generate_comprehensive_report(project_id)
            
            Clock.schedule_once(
                lambda dt: self._handle_comprehensive_report_results(results), 0
            )
        except Exception as e:
            print(f"Error in comprehensive report: {e}")
            Clock.schedule_once(
                lambda dt: toast("Comprehensive report generation failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _handle_comprehensive_report_results(self, results: Dict):
        """Handle comprehensive report results - delegate to UI"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Report Error: {error_msg}")
            return
        
        # Delegate to analytics screen to handle UI display
        self.analytics_screen.display_comprehensive_report_results(results)
    
    def show_variable_selection(self, project_id: str):
        """Show variable selection interface - delegate to UI"""
        self.analytics_screen.show_descriptive_variable_selection_ui(project_id)
    
    def show_sample_size_recommendations(self, project_id: str):
        """Show sample size recommendations - delegate to UI"""
        recommendations = self.get_sample_size_recommendations(project_id)
        self.analytics_screen.show_sample_size_recommendations_ui(recommendations)
    
    def export_analysis_results(self, results: Dict, analysis_name: str):
        """Export analysis results"""
        try:
            export_path = self.analytics_service.export_analysis_results(results, 'json')
            toast(f"{analysis_name} results exported to: {export_path}")
        except Exception as e:
            toast(f"Export failed: {str(e)}")
    
    def export_sample_size_analysis(self, sample_adequacy: dict):
        """Export sample size analysis results"""
        try:
            import json
            analysis_json = json.dumps(sample_adequacy, indent=2, default=str)
            toast("Sample size analysis exported successfully!")
            print("Sample Size Analysis Export:")
            print(analysis_json)
        except Exception as e:
            toast(f"Export failed: {str(e)}")
    
    def update_variable_selection(self, variable: str, active: bool):
        """Update variable selection state"""
        if active and variable not in self.selected_variables:
            self.selected_variables.append(variable)
        elif not active and variable in self.selected_variables:
            self.selected_variables.remove(variable)
    
    def run_analysis_with_selected_vars(self):
        """Run analysis with selected variables"""
        if not self.selected_variables:
            toast("Please select at least one variable")
            return
        
        if not self.analytics_screen.current_project_id:
            toast("Please select a project first")
            return
        
        # Run analysis with selected variables
        self.run_descriptive_analysis(
            self.analytics_screen.current_project_id,
            {'variables': self.selected_variables}
        )