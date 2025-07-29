"""
Distribution Analytics Handler
Specialized service for distribution analysis and statistical testing
"""

from typing import Dict, List, Any, Optional
import threading
import urllib.parse
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class DistributionAnalyticsHandler:
    """Handler for distribution analysis operations - Business Logic Only"""
    
    def __init__(self, analytics_service, screen):
        self.analytics_service = analytics_service
        self.screen = screen
        self.selected_variables = []
    
    def run_distribution_analysis(self, project_id: str, variables: Optional[List[str]] = None):
        """Run distribution analysis for selected variables"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_distribution_thread,
            args=(project_id, variables),
            daemon=True
        ).start()
    
    def _run_distribution_thread(self, project_id: str, variables: Optional[List[str]]):
        """Background thread for distribution analysis"""
        try:
            # Run distribution analysis
            results = self.analytics_service.run_distribution_analysis(project_id, variables)
            
            Clock.schedule_once(
                lambda dt: self._handle_distribution_results(results), 0
            )
        except Exception as e:
            print(f"Error in distribution analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Distribution analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_distribution_results(self, results):
        """Handle distribution analysis results - delegate to UI"""
        print(f"[DEBUG] Distribution results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                toast("Backend connection error")
            else:
                toast(f"Analysis Error: {error_msg}")
            return
        
        # Delegate to screen to handle UI display
        self.screen.display_distribution_results(results)
    
    def get_distribution_summary_data(self, summary: Dict) -> Dict:
        """Extract summary data for UI consumption"""
        return {
            'variables_analyzed': summary.get('variables_analyzed', 'N/A'),
            'observations': summary.get('observations', 'N/A'),
            'analysis_methods': 'Normality tests, skewness, kurtosis, outlier detection'
        }
    
    def get_variable_distribution_data(self, variable: str, analysis: Dict) -> Dict:
        """Extract variable distribution data for UI consumption"""
        dist_analysis = analysis.get('distribution_analysis', {})
        normality_test = analysis.get('normality_test', {})
        skew_kurt = analysis.get('skewness_kurtosis', {})
        outliers = analysis.get('outliers', {})
        
        return {
            'variable_name': variable,
            'distribution_type': dist_analysis.get('likely_distribution', 'Unknown'),
            'normality_p_value': normality_test.get('p_value', 'N/A'),
            'skewness': skew_kurt.get('skewness', 'N/A'),
            'kurtosis': skew_kurt.get('kurtosis', 'N/A'),
            'outlier_count': len(outliers.get('outlier_indices', [])),
            'outlier_percentage': outliers.get('outlier_percentage', 0),
            'outlier_values': outliers.get('outlier_values', [])
        }
    
    def get_variable_details_text(self, variable: str, analysis: Dict) -> str:
        """Generate detailed analysis text for a variable"""
        details_text = f"Detailed Analysis for {variable}\n\n"
        
        # Distribution analysis
        if 'distribution_analysis' in analysis:
            dist = analysis['distribution_analysis']
            details_text += "Distribution Analysis:\n"
            details_text += f"• Likely Distribution: {dist.get('likely_distribution', 'Unknown')}\n"
            details_text += f"• Goodness of Fit: {dist.get('goodness_of_fit', 'N/A')}\n\n"
        
        # Normality test
        if 'normality_test' in analysis:
            norm = analysis['normality_test']
            details_text += "Normality Test:\n"
            details_text += f"• Test Statistic: {norm.get('statistic', 'N/A')}\n"
            details_text += f"• P-value: {norm.get('p_value', 'N/A')}\n"
            details_text += f"• Is Normal: {'Yes' if norm.get('is_normal', False) else 'No'}\n\n"
        
        # Skewness and Kurtosis
        if 'skewness_kurtosis' in analysis:
            sk = analysis['skewness_kurtosis']
            details_text += "Shape Statistics:\n"
            details_text += f"• Skewness: {sk.get('skewness', 'N/A'):.4f}\n"
            details_text += f"• Kurtosis: {sk.get('kurtosis', 'N/A'):.4f}\n"
            details_text += f"• Interpretation: {sk.get('interpretation', 'N/A')}\n"
        
        return details_text
    
    def get_outliers_details_text(self, variable: str, outliers: Dict) -> str:
        """Generate outliers details text for a variable"""
        outlier_indices = outliers.get('outlier_indices', [])
        outlier_values = outliers.get('outlier_values', [])
        
        details_text = f"Outliers in {variable}\n\n"
        details_text += f"Total Outliers: {len(outlier_indices)}\n"
        details_text += f"Percentage: {outliers.get('outlier_percentage', 0):.2f}%\n\n"
        
        if outlier_values:
            details_text += "Outlier Values:\n"
            for i, value in enumerate(outlier_values[:10]):  # Show first 10
                details_text += f"• {value}\n"
            
            if len(outlier_values) > 10:
                details_text += f"... and {len(outlier_values) - 10} more\n"
        
        return details_text
    
    def get_additional_analysis_options(self) -> List[Dict]:
        """Get additional analysis options for distribution data"""
        return [
            {"code": "outlier", "title": "Detailed Outlier Analysis", "description": "Advanced outlier detection methods"},
            {"code": "categorical", "title": "Categorical Analysis", "description": "If variables have categories"},
            {"code": "correlation", "title": "Correlation Analysis", "description": "Variable relationships"},
            {"code": "quality", "title": "Data Quality Check", "description": "Assess data completeness"},
        ]
    
    def run_additional_analysis(self, analysis_type: str):
        """Run additional analysis type"""
        project_id = self.screen.current_project_id
        if not project_id:
            toast("Please select a project first")
            return
        
        toast(f"Running {analysis_type} analysis...")
        
        if analysis_type == "outlier":
            self.analytics_service.run_outlier_analysis(project_id)
        elif analysis_type == "categorical":
            self.analytics_service.run_categorical_analysis(project_id)
        elif analysis_type == "correlation":
            self.analytics_service.run_analysis(project_id, "correlation")
        elif analysis_type == "quality":
            self.analytics_service.run_data_quality_analysis(project_id)
    
    def export_results(self, results: Dict):
        """Export distribution analysis results"""
        try:
            exported = self.analytics_service.export_analysis_results(results, 'json')
            toast("Distribution analysis results exported")
        except Exception as e:
            toast(f"Export failed: {str(e)}")
    
    def show_variable_selection_for_distribution(self, project_id: str):
        """Show variable selection dialog specifically for distribution analysis"""
        # Get project variables
        threading.Thread(
            target=self._load_variables_for_selection,
            args=(project_id,),
            daemon=True
        ).start()
    
    def _load_variables_for_selection(self, project_id: str):
        """Load variables for selection dialog"""
        try:
            variables = self.analytics_service.get_project_variables(project_id)
            Clock.schedule_once(
                lambda dt: self._handle_variables_for_selection(variables), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: toast("Error loading variables"), 0
            )
    
    def _handle_variables_for_selection(self, variables: Dict):
        """Handle variables for selection - delegate to UI"""
        if 'error' in variables:
            toast("Error loading project variables")
            return
        
        # Extract numeric variables for distribution analysis
        numeric_vars = variables.get('numeric_variables', [])
        
        # Delegate to screen to handle UI
        self.screen.show_distribution_variable_selection(numeric_vars)
    
    def update_variable_selection(self, variable: str, active: bool):
        """Update selected variables list"""
        if active and variable not in self.selected_variables:
            self.selected_variables.append(variable)
        elif not active and variable in self.selected_variables:
            self.selected_variables.remove(variable)
    
    def run_distribution_with_selected_vars(self):
        """Run distribution analysis with selected variables"""
        if not self.selected_variables:
            toast("Please select at least one variable")
            return
        
        project_id = self.screen.current_project_id
        if not project_id:
            toast("No project selected")
            return
        
        toast(f"Running distribution analysis on {len(self.selected_variables)} variables...")
        self.run_distribution_analysis(project_id, self.selected_variables)

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

    def run_normality_test_backend(self, project_id: str, variables: List[str]) -> Dict:
        """Run normality tests for specified variables via backend"""
        try:
            request_data = {
                'test_type': 'normality',
                'variables': variables
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/distributions', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Normality test failed: {str(e)}'}

    def run_outlier_detection_backend(self, project_id: str, variables: Optional[List[str]] = None, 
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
            return {'error': f'Outlier detection failed: {str(e)}'}

    def run_skewness_kurtosis_backend(self, project_id: str, variables: List[str]) -> Dict:
        """Run skewness and kurtosis analysis via backend"""
        try:
            request_data = {
                'analysis_type': 'shape_statistics',
                'variables': variables
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/distributions', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Skewness/Kurtosis analysis failed: {str(e)}'}

    def run_goodness_of_fit_backend(self, project_id: str, variable: str, distribution: str = 'normal') -> Dict:
        """Run goodness of fit test for a specific distribution via backend"""
        try:
            request_data = {
                'test_type': 'goodness_of_fit',
                'variable': variable,
                'distribution': distribution
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/distributions', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Goodness of fit test failed: {str(e)}'} 