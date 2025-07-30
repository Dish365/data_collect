"""
Categorical Analytics Handler
Specialized service for categorical data analysis and chi-square tests
"""

from typing import Dict, List, Any, Optional
import threading
import urllib.parse
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class CategoricalAnalyticsHandler:
    """Handler for categorical analysis operations - Business Logic Only"""
    
    def __init__(self, analytics_service, screen):
        self.analytics_service = analytics_service
        self.screen = screen
        self.selected_variables = []
    
    def run_categorical_analysis(self, project_id: str, variables: Optional[List[str]] = None):
        """Run categorical analysis for selected variables"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_categorical_thread,
            args=(project_id, variables),
            daemon=True
        ).start()
    
    def _run_categorical_thread(self, project_id: str, variables: Optional[List[str]]):
        """Background thread for categorical analysis"""
        try:
            # Run categorical analysis
            results = self.analytics_service.run_categorical_analysis(project_id, variables)
            
            Clock.schedule_once(
                lambda dt: self._handle_categorical_results(results), 0
            )
        except Exception as e:
            print(f"Error in categorical analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Categorical analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_categorical_results(self, results):
        """Handle categorical analysis results - delegate to UI"""
        print(f"[DEBUG] Categorical results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                toast("Backend connection error")
            else:
                toast(f"Analysis Error: {error_msg}")
            return
        
        # Delegate to screen to handle UI display
        self.screen.display_categorical_results(results)
    
    def get_categorical_summary_data(self, summary: Dict) -> Dict:
        """Extract summary data for UI consumption"""
        return {
            'variables_analyzed': summary.get('variables_analyzed', 'N/A'),
            'observations': summary.get('observations', 'N/A'),
            'cross_tabs_computed': summary.get('cross_tabs_computed', 'N/A'),
            'analysis_methods': 'Frequency analysis, chi-square tests, Cramer\'s V'
        }
    
    def get_variable_categorical_data(self, variable: str, analysis: Dict) -> Dict:
        """Extract variable analysis data for UI consumption"""
        return {
            'variable_name': variable,
            'unique_count': analysis.get('unique', 'N/A'),
            'most_common': analysis.get('top', 'N/A'),
            'most_common_freq': analysis.get('freq', 'N/A'),
            'missing_count': analysis.get('missing', 0),
            'value_counts': analysis.get('value_counts', {}),
            'has_distribution': 'value_counts' in analysis
        }
    
    def get_cross_tabulation_data(self, cross_tabs: Dict) -> List[Dict]:
        """Extract cross-tabulation data for UI consumption"""
        cross_tab_data = []
        
        for cross_tab_name, cross_tab_data in cross_tabs.items():
            if 'error' not in cross_tab_data:
                chi_square = cross_tab_data.get('chi_square_test', {})
                cramers_v = cross_tab_data.get('cramers_v', 'N/A')
                
                cross_tab_data.append({
                    'name': cross_tab_name.replace('_vs_', ' vs ').title(),
                    'chi_square_statistic': chi_square.get('statistic', 'N/A'),
                    'chi_square_p_value': chi_square.get('p_value', 'N/A'),
                    'cramers_v': cramers_v
                })
        
        return cross_tab_data
    
    def get_variable_details_text(self, variable: str, analysis: Dict) -> str:
        """Get detailed text analysis for a variable"""
        details = f"Detailed Analysis for {variable}\n\n"
        
        if 'value_counts' in analysis:
            details += "Category Distribution:\n"
            for category, count in analysis['value_counts'].items():
                details += f"  • {category}: {count}\n"
        
        if 'missing' in analysis:
            details += f"\nMissing Values: {analysis['missing']}\n"
        
        if 'unique' in analysis:
            details += f"Unique Categories: {analysis['unique']}\n"
        
        if 'top' in analysis and 'freq' in analysis:
            details += f"Most Common: {analysis['top']} ({analysis['freq']} occurrences)\n"
        
        return details
    
    def get_distribution_details_text(self, variable: str, analysis: Dict) -> str:
        """Get distribution details text for a variable"""
        details = f"Distribution Analysis for {variable}\n\n"
        
        if 'value_counts' in analysis:
            total = sum(analysis['value_counts'].values())
            details += "Category Distribution:\n"
            
            # Sort by frequency
            sorted_counts = sorted(analysis['value_counts'].items(), 
                                key=lambda x: x[1], reverse=True)
            
            for category, count in sorted_counts:
                percentage = (count / total) * 100 if total > 0 else 0
                details += f"  • {category}: {count} ({percentage:.1f}%)\n"
        
        return details
    
    def get_additional_analysis_options(self) -> List[Dict]:
        """Get additional analysis options"""
        return [
            {
                'title': 'Chi-Square Test',
                'description': 'Test for independence between categorical variables',
                'code': 'chi_square'
            },
            {
                'title': 'Cramer\'s V Analysis',
                'description': 'Measure strength of association between variables',
                'code': 'cramers_v'
            },
            {
                'title': 'Frequency Analysis',
                'description': 'Detailed frequency distribution analysis',
                'code': 'frequency'
            }
        ]
    
    def run_additional_analysis(self, analysis_type: str):
        """Run additional categorical analysis"""
        if not self.screen.current_project_id:
            toast("Please select a project first")
            return
        
        # Delegate to screen to handle UI and run analysis
        self.screen.run_categorical_additional_analysis(analysis_type)
    
    def export_results(self, results: Dict):
        """Export categorical analysis results"""
        try:
            # Delegate to analytics service for export
            export_path = self.analytics_service.export_analysis_results(results, 'json')
            toast(f"Results exported to: {export_path}")
        except Exception as e:
            toast(f"Export failed: {str(e)}")
    
    def show_variable_selection_for_categorical(self, project_id: str):
        """Show variable selection interface - delegate to UI"""
        self.screen.show_categorical_variable_selection_ui(project_id)
    
    def _load_variables_for_selection(self, project_id: str):
        """Load variables for selection"""
        try:
            variables = self.analytics_service.get_project_variables(project_id)
            Clock.schedule_once(
                lambda dt: self._handle_variables_for_selection(variables), 0
            )
        except Exception as e:
            print(f"Error loading variables: {e}")
            Clock.schedule_once(
                lambda dt: toast("Error loading variables"), 0
            )
    
    def _handle_variables_for_selection(self, variables: Dict):
        """Handle variables for selection"""
        if not variables or 'error' in variables:
            toast("No variables available for analysis")
            return
        
        categorical_vars = variables.get('categorical', [])
        self.screen.show_categorical_variable_selection(categorical_vars)
    
    def update_variable_selection(self, variable: str, active: bool):
        """Update variable selection state"""
        if active and variable not in self.selected_variables:
            self.selected_variables.append(variable)
        elif not active and variable in self.selected_variables:
            self.selected_variables.remove(variable)
    
    def run_categorical_with_selected_vars(self):
        """Run categorical analysis with selected variables"""
        if not self.selected_variables:
            toast("Please select at least one variable")
            return
        
        if not self.screen.current_project_id:
            toast("Please select a project first")
            return
        
        self.run_categorical_analysis(
            self.screen.current_project_id, 
            self.selected_variables
        )

    # New Advanced Categorical Analytics Methods

    def run_cross_tabulation(self, project_id: str, var1: str, var2: str, 
                            normalize: Optional[str] = None):
        """Run cross-tabulation analysis between two categorical variables"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_cross_tabulation_thread,
            args=(project_id, var1, var2, normalize),
            daemon=True
        ).start()

    def _run_cross_tabulation_thread(self, project_id: str, var1: str, var2: str, 
                                    normalize: Optional[str]):
        """Background thread for cross-tabulation analysis"""
        try:
            results = self.analytics_service.run_cross_tabulation_backend(
                project_id, var1, var2, normalize
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_cross_tabulation_results(results), 0
            )
        except Exception as e:
            print(f"Error in cross-tabulation analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Cross-tabulation analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_cross_tabulation_results(self, results):
        """Handle cross-tabulation analysis results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Cross-tabulation Error: {error_msg}")
            return
        
        self.screen.display_cross_tabulation_results(results)

    def run_diversity_metrics(self, project_id: str, variables: Optional[List[str]] = None):
        """Run diversity metrics analysis for categorical variables"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_diversity_metrics_thread,
            args=(project_id, variables),
            daemon=True
        ).start()

    def _run_diversity_metrics_thread(self, project_id: str, variables: Optional[List[str]]):
        """Background thread for diversity metrics analysis"""
        try:
            results = self.analytics_service.run_diversity_metrics_backend(
                project_id, variables
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_diversity_metrics_results(results), 0
            )
        except Exception as e:
            print(f"Error in diversity metrics analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Diversity metrics analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_diversity_metrics_results(self, results):
        """Handle diversity metrics analysis results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Diversity Metrics Error: {error_msg}")
            return
        
        self.screen.display_diversity_metrics_results(results)

    def run_categorical_associations(self, project_id: str, variables: Optional[List[str]] = None,
                                   method: str = 'cramers_v'):
        """Run categorical associations analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_categorical_associations_thread,
            args=(project_id, variables, method),
            daemon=True
        ).start()

    def _run_categorical_associations_thread(self, project_id: str, variables: Optional[List[str]], 
                                           method: str):
        """Background thread for categorical associations analysis"""
        try:
            results = self.analytics_service.run_categorical_associations_backend(
                project_id, variables, method
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_categorical_associations_results(results), 0
            )
        except Exception as e:
            print(f"Error in categorical associations analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Categorical associations analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )

    def _handle_categorical_associations_results(self, results):
        """Handle categorical associations analysis results"""
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            toast(f"Categorical Associations Error: {error_msg}")
            return
        
        self.screen.display_categorical_associations_results(results)

    # Data extraction methods for new analyses

    def get_cross_tabulation_data(self, cross_tab_data: Dict) -> Dict:
        """Extract cross-tabulation data for UI consumption"""
        if 'error' in cross_tab_data:
            return {
                'has_error': True,
                'error_message': cross_tab_data['error']
            }
        
        results = cross_tab_data.get('results', {})
        
        return {
            'has_error': False,
            'var1': cross_tab_data.get('var1', 'Variable 1'),
            'var2': cross_tab_data.get('var2', 'Variable 2'),
            'crosstab': results.get('crosstab', {}),
            'row_percentages': results.get('row_percentages', {}),
            'column_percentages': results.get('column_percentages', {}),
            'chi_square': results.get('chi_square', {}),
            'grand_total': results.get('grand_total', 0)
        }

    def get_diversity_metrics_data(self, diversity_data: Dict) -> Dict:
        """Extract diversity metrics data for UI consumption"""
        if 'error' in diversity_data:
            return {
                'has_error': True,
                'error_message': diversity_data['error']
            }
        
        results = diversity_data.get('results', {})
        
        return {
            'has_error': False,
            'metrics_by_variable': results,
            'total_variables': len(results)
        }

    def get_categorical_associations_data(self, associations_data: Dict) -> Dict:
        """Extract categorical associations data for UI consumption"""
        if 'error' in associations_data:
            return {
                'has_error': True,
                'error_message': associations_data['error']
            }
        
        results = associations_data.get('results', {})
        method = associations_data.get('method', 'cramers_v')
        
        return {
            'has_error': False,
            'method': method,
            'association_matrix': results,
            'variables_analyzed': len(results) if isinstance(results, dict) else 0
        }

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

    def run_chi_square_test_backend(self, project_id: str, var1: str, var2: str) -> Dict:
        """Run chi-square test between two categorical variables via backend"""
        try:
            request_data = {
                'test_type': 'chi_square',
                'variable1': var1,
                'variable2': var2
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/categorical', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Chi-square test failed: {str(e)}'}

    def run_cramers_v_analysis_backend(self, project_id: str, variables: List[str]) -> Dict:
        """Run Cramer's V analysis for categorical variables via backend"""
        try:
            request_data = {
                'analysis_type': 'cramers_v',
                'variables': variables
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/categorical', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Cramers V analysis failed: {str(e)}'}

    def run_frequency_analysis_backend(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run detailed frequency analysis via backend"""
        try:
            request_data = {
                'analysis_type': 'frequency',
                'variables': variables or []
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/categorical', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Frequency analysis failed: {str(e)}'}

    # New Advanced Categorical Analytics Backend Methods

    def run_cross_tabulation_backend(self, project_id: str, var1: str, var2: str, 
                                    normalize: Optional[str] = None) -> Dict:
        """Run cross-tabulation analysis via backend"""
        try:
            request_data = {
                'var1': var1,
                'var2': var2
            }
            if normalize:
                request_data['normalize'] = normalize
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/cross-tabulation', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Cross-tabulation analysis failed: {str(e)}'}

    def run_diversity_metrics_backend(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run diversity metrics analysis via backend"""
        try:
            request_data = {}
            if variables:
                request_data['variables'] = variables
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/diversity-metrics', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Diversity metrics analysis failed: {str(e)}'}

    def run_categorical_associations_backend(self, project_id: str, variables: Optional[List[str]] = None,
                                           method: str = 'cramers_v') -> Dict:
        """Run categorical associations analysis via backend"""
        try:
            request_data = {
                'method': method
            }
            if variables:
                request_data['variables'] = variables
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/categorical-associations', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Categorical associations analysis failed: {str(e)}'} 