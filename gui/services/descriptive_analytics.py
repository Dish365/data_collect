"""
Descriptive Analytics Handler
Specialized service for descriptive statistics and data analysis
"""

from typing import Dict, List, Any, Optional, Union
import threading
import urllib.parse
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class DescriptiveAnalyticsHandler:
    """Handler for descriptive analytics operations - Business Logic Only"""
    
    def __init__(self, analytics_service, screen):
        self.analytics_service = analytics_service
        self.screen = screen
        self.selected_variables = []
    
    def run_descriptive_analysis(self, project_id: str, analysis_config: Dict = None):
        """Run descriptive analysis for the project"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
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
                lambda dt: self.screen.set_loading(False), 0
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
        
        # Delegate to screen to handle UI display
        self.screen.display_descriptive_results(results)
    
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
        
        self.screen.set_loading(True)
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
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_specific_analysis_results(self, results: Dict, analysis_name: str):
        """Handle specific analysis results - delegate to UI"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"{analysis_name} Error: {error_msg}")
            return
        
        # Delegate to screen to handle UI display
        self.screen.display_specific_analysis_results(results, analysis_name)
    
    def run_comprehensive_report(self, project_id: str):
        """Run comprehensive descriptive report"""
        print(f"[DEBUG] Running comprehensive report for project {project_id}")
        toast("Generating comprehensive report...")
        
        self.screen.set_loading(True)
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
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_comprehensive_report_results(self, results: Dict):
        """Handle comprehensive report results - delegate to UI"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Report Error: {error_msg}")
            return
        
        # Delegate to screen to handle UI display
        self.screen.display_comprehensive_report_results(results)
    
    def show_variable_selection(self, project_id: str):
        """Show variable selection interface - delegate to UI"""
        self.screen.show_descriptive_variable_selection_ui(project_id)
    
    def show_sample_size_recommendations(self, project_id: str):
        """Show sample size recommendations - delegate to UI"""
        recommendations = self.get_sample_size_recommendations(project_id)
        self.screen.show_sample_size_recommendations_ui(recommendations)
    
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
        
        if not self.screen.current_project_id:
            toast("Please select a project first")
            return
        
        # Run analysis with selected variables
        self.run_descriptive_analysis(
            self.screen.current_project_id,
            {'variables': self.selected_variables}
        )

    # New Advanced Analytics Methods

    def run_geospatial_analysis(self, project_id: str, lat_column: str, lon_column: str,
                               value_column: Optional[str] = None, max_distance_km: float = 10.0,
                               n_clusters: int = 5):
        """Run geospatial analysis for the project"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_geospatial_thread,
            args=(project_id, lat_column, lon_column, value_column, max_distance_km, n_clusters),
            daemon=True
        ).start()

    def _run_geospatial_thread(self, project_id: str, lat_column: str, lon_column: str,
                              value_column: Optional[str], max_distance_km: float, n_clusters: int):
        """Background thread for geospatial analysis"""
        try:
            results = self.analytics_service.run_geospatial_analysis_backend(
                project_id, lat_column, lon_column, value_column, max_distance_km, n_clusters
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_geospatial_results(results), 0
            )
        except Exception as e:
            print(f"Error in geospatial analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Geospatial analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_geospatial_results(self, results):
        """Handle geospatial analysis results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Geospatial Error: {error_msg}")
            return
        
        self.screen.display_geospatial_results(results)

    def run_temporal_analysis(self, project_id: str, date_column: str,
                             value_columns: Optional[List[str]] = None, 
                             detect_seasonal: bool = True,
                             seasonal_period: Optional[int] = None):
        """Run temporal analysis for the project"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_temporal_thread,
            args=(project_id, date_column, value_columns, detect_seasonal, seasonal_period),
            daemon=True
        ).start()

    def _run_temporal_thread(self, project_id: str, date_column: str,
                            value_columns: Optional[List[str]], detect_seasonal: bool, 
                            seasonal_period: Optional[int]):
        """Background thread for temporal analysis"""
        try:
            results = self.analytics_service.run_temporal_analysis_backend(
                project_id, date_column, value_columns, detect_seasonal, seasonal_period
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_temporal_results(results), 0
            )
        except Exception as e:
            print(f"Error in temporal analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Temporal analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_temporal_results(self, results):
        """Handle temporal analysis results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Temporal Error: {error_msg}")
            return
        
        self.screen.display_temporal_results(results)

    def run_weighted_statistics(self, project_id: str, value_column: str, weight_column: str):
        """Run weighted statistics analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_weighted_stats_thread,
            args=(project_id, value_column, weight_column),
            daemon=True
        ).start()

    def _run_weighted_stats_thread(self, project_id: str, value_column: str, weight_column: str):
        """Background thread for weighted statistics"""
        try:
            results = self.analytics_service.run_weighted_statistics_backend(
                project_id, value_column, weight_column
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_weighted_stats_results(results), 0
            )
        except Exception as e:
            print(f"Error in weighted statistics: {e}")
            Clock.schedule_once(
                lambda dt: toast("Weighted statistics failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_weighted_stats_results(self, results):
        """Handle weighted statistics results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Weighted Stats Error: {error_msg}")
            return
        
        self.screen.display_weighted_statistics_results(results)

    def run_grouped_statistics(self, project_id: str, group_by: Union[str, List[str]],
                              target_columns: Optional[List[str]] = None,
                              stats_functions: Optional[List[str]] = None):
        """Run grouped statistics analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_grouped_stats_thread,
            args=(project_id, group_by, target_columns, stats_functions),
            daemon=True
        ).start()

    def _run_grouped_stats_thread(self, project_id: str, group_by: Union[str, List[str]],
                                 target_columns: Optional[List[str]], stats_functions: Optional[List[str]]):
        """Background thread for grouped statistics"""
        try:
            results = self.analytics_service.run_grouped_statistics_backend(
                project_id, group_by, target_columns, stats_functions
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_grouped_stats_results(results), 0
            )
        except Exception as e:
            print(f"Error in grouped statistics: {e}")
            Clock.schedule_once(
                lambda dt: toast("Grouped statistics failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_grouped_stats_results(self, results):
        """Handle grouped statistics results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Grouped Stats Error: {error_msg}")
            return
        
        self.screen.display_grouped_statistics_results(results)

    def run_missing_patterns_analysis(self, project_id: str, max_patterns: int = 20,
                                     group_column: Optional[str] = None):
        """Run missing data patterns analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_missing_patterns_thread,
            args=(project_id, max_patterns, group_column),
            daemon=True
        ).start()

    def _run_missing_patterns_thread(self, project_id: str, max_patterns: int, group_column: Optional[str]):
        """Background thread for missing patterns analysis"""
        try:
            results = self.analytics_service.run_missing_patterns_analysis_backend(
                project_id, max_patterns, group_column
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_missing_patterns_results(results), 0
            )
        except Exception as e:
            print(f"Error in missing patterns analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Missing patterns analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_missing_patterns_results(self, results):
        """Handle missing patterns results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Missing Patterns Error: {error_msg}")
            return
        
        self.screen.display_missing_patterns_results(results)

    def generate_executive_summary(self, project_id: str):
        """Generate executive summary"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._generate_executive_summary_thread,
            args=(project_id,),
            daemon=True
        ).start()

    def _generate_executive_summary_thread(self, project_id: str):
        """Background thread for executive summary"""
        try:
            results = self.analytics_service.generate_executive_summary_backend(project_id)
            
            Clock.schedule_once(
                lambda dt: self._handle_executive_summary_results(results), 0
            )
        except Exception as e:
            print(f"Error in executive summary: {e}")
            Clock.schedule_once(
                lambda dt: toast("Executive summary generation failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_executive_summary_results(self, results):
        """Handle executive summary results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Executive Summary Error: {error_msg}")
            return
        
        self.screen.display_executive_summary_results(results)

    def export_analysis_report(self, project_id: str, format: str = 'json',
                              analysis_type: str = 'comprehensive',
                              include_metadata: bool = True):
        """Export analysis report"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._export_report_thread,
            args=(project_id, format, analysis_type, include_metadata),
            daemon=True
        ).start()

    def _export_report_thread(self, project_id: str, format: str, analysis_type: str, include_metadata: bool):
        """Background thread for report export"""
        try:
            results = self.analytics_service.export_analysis_report_backend(
                project_id, format, analysis_type, include_metadata
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_export_report_results(results, format), 0
            )
        except Exception as e:
            print(f"Error in report export: {e}")
            Clock.schedule_once(
                lambda dt: toast("Report export failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_export_report_results(self, results, format: str):
        """Handle export report results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Export Error: {error_msg}")
            return
        
        self.screen.display_export_report_results(results, format)

    # Analytics backend methods
    def _make_analytics_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to analytics backend"""
        try:
            import requests
            base_url = "http://127.0.0.1:8001"
            url = f"{base_url}/api/v1/analytics/descriptive/{endpoint}"
            
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'DataCollect-GUI/1.0'
            })
            
            if method == 'GET':
                response = session.get(url, timeout=30)
            elif method == 'POST':
                if data:
                    response = session.post(url, json=data, timeout=60)
                else:
                    response = session.post(url, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and 'status' in result:
                    if result['status'] == 'success':
                        return result.get('data', {})
                    else:
                        return {'error': result.get('message', 'Unknown error')}
                return result
            else:
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get('detail', f'HTTP {response.status_code}')
                    return {'error': error_msg}
                except:
                    return {'error': f'HTTP {response.status_code}: {response.text}'}
                
        except Exception as e:
            return {'error': f'Request error: {str(e)}'}

    def run_descriptive_analysis_backend(self, project_id: str, analysis_type: str = "descriptive", 
                                       target_variables: Optional[List[str]] = None) -> Dict:
        """Run descriptive analysis using the analytics backend"""
        try:
            params = [('analysis_type', analysis_type)]
            if target_variables and isinstance(target_variables, list):
                for var in target_variables:
                    params.append(('target_variables', var))
            elif target_variables:
                params.append(('target_variables', target_variables))
            
            url = f"project/{project_id}/analyze"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Descriptive analysis failed: {str(e)}'}

    def run_basic_statistics_backend(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run basic statistical analysis via backend"""
        try:
            params = []
            if variables and isinstance(variables, list):
                for var in variables:
                    params.append(('variables', var))
            elif variables:
                params.append(('variables', variables))
            
            url = f'project/{project_id}/analyze/basic-statistics'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Basic statistics failed: {str(e)}'}

    def run_distribution_analysis_backend(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run distribution analysis via backend"""
        try:
            params = []
            if variables and isinstance(variables, list):
                for var in variables:
                    params.append(('variables', var))
            elif variables:
                params.append(('variables', variables))
            
            url = f'project/{project_id}/analyze/distributions'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Distribution analysis failed: {str(e)}'}

    def run_categorical_analysis_backend(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run categorical analysis via backend"""
        try:
            params = []
            if variables and isinstance(variables, list):
                for var in variables:
                    params.append(('variables', var))
            elif variables:
                params.append(('variables', variables))
            
            url = f'project/{project_id}/analyze/categorical'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Categorical analysis failed: {str(e)}'}

    def run_outlier_analysis_backend(self, project_id: str, variables: Optional[List[str]] = None, 
                                   methods: Optional[List[str]] = None) -> Dict:
        """Run outlier detection analysis via backend"""
        try:
            request_data = {}
            if variables:
                request_data['variables'] = variables
            if methods:
                request_data['methods'] = methods
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/outliers', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Outlier analysis failed: {str(e)}'}

    def run_missing_data_analysis_backend(self, project_id: str) -> Dict:
        """Run missing data analysis via backend"""
        try:
            result = self._make_analytics_request(f'project/{project_id}/analyze/missing-data', 
                                                method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Missing data analysis failed: {str(e)}'}

    def run_data_quality_analysis_backend(self, project_id: str) -> Dict:
        """Run data quality analysis via backend"""
        try:
            result = self._make_analytics_request(f'project/{project_id}/analyze/data-quality', 
                                                method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Data quality analysis failed: {str(e)}'}

    def generate_comprehensive_report_backend(self, project_id: str, include_plots: bool = False) -> Dict:
        """Generate comprehensive analytics report via backend"""
        try:
            request_data = {'include_plots': include_plots}
            
            result = self._make_analytics_request(f'project/{project_id}/generate-report', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Report generation failed: {str(e)}'}

    # New Advanced Analytics Backend Methods
    
    def run_geospatial_analysis_backend(self, project_id: str, lat_column: str, lon_column: str,
                                       value_column: Optional[str] = None, max_distance_km: float = 10.0,
                                       n_clusters: int = 5) -> Dict:
        """Run geospatial analysis via backend"""
        try:
            request_data = {
                'lat_column': lat_column,
                'lon_column': lon_column,
                'max_distance_km': max_distance_km,
                'n_clusters': n_clusters
            }
            if value_column:
                request_data['value_column'] = value_column
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/geospatial', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Geospatial analysis failed: {str(e)}'}

    def run_temporal_analysis_backend(self, project_id: str, date_column: str,
                                     value_columns: Optional[List[str]] = None, 
                                     detect_seasonal: bool = True,
                                     seasonal_period: Optional[int] = None) -> Dict:
        """Run temporal analysis via backend"""
        try:
            request_data = {
                'date_column': date_column,
                'detect_seasonal': detect_seasonal
            }
            if value_columns:
                request_data['value_columns'] = value_columns
            if seasonal_period:
                request_data['seasonal_period'] = seasonal_period
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/temporal', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Temporal analysis failed: {str(e)}'}

    def run_weighted_statistics_backend(self, project_id: str, value_column: str, weight_column: str) -> Dict:
        """Run weighted statistics analysis via backend"""
        try:
            request_data = {
                'value_column': value_column,
                'weight_column': weight_column
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/weighted-statistics', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Weighted statistics failed: {str(e)}'}

    def run_grouped_statistics_backend(self, project_id: str, group_by: Union[str, List[str]],
                                      target_columns: Optional[List[str]] = None,
                                      stats_functions: Optional[List[str]] = None) -> Dict:
        """Run grouped statistics analysis via backend"""
        try:
            request_data = {
                'group_by': group_by
            }
            if target_columns:
                request_data['target_columns'] = target_columns
            if stats_functions:
                request_data['stats_functions'] = stats_functions
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/grouped-statistics', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Grouped statistics failed: {str(e)}'}

    def run_missing_patterns_analysis_backend(self, project_id: str, max_patterns: int = 20,
                                            group_column: Optional[str] = None) -> Dict:
        """Run missing data patterns analysis via backend"""
        try:
            request_data = {
                'max_patterns': max_patterns
            }
            if group_column:
                request_data['group_column'] = group_column
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/missing-patterns', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Missing patterns analysis failed: {str(e)}'}

    def generate_executive_summary_backend(self, project_id: str) -> Dict:
        """Generate executive summary via backend"""
        try:
            result = self._make_analytics_request(f'project/{project_id}/generate-executive-summary', 
                                                method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Executive summary generation failed: {str(e)}'}

    def export_analysis_report_backend(self, project_id: str, format: str = 'json',
                                      analysis_type: str = 'comprehensive',
                                      include_metadata: bool = True) -> Dict:
        """Export analysis report via backend"""
        try:
            request_data = {
                'format': format,
                'analysis_type': analysis_type,
                'include_metadata': include_metadata
            }
            
            result = self._make_analytics_request(f'project/{project_id}/export-report', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Report export failed: {str(e)}'}