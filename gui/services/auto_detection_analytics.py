"""
Auto Detection Analytics Handler
Specialized service for intelligent auto-detection analysis - Business Logic Only
"""

from typing import Dict, List, Any, Optional
import threading
import json
import urllib.parse
from datetime import datetime
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class AutoDetectionAnalyticsHandler:
    """Handler for auto-detection analytics operations - Business Logic Only"""
    
    def __init__(self, analytics_service, screen):
        self.analytics_service = analytics_service
        self.screen = screen
        
        # Analysis state
        self.current_results = {}
        self.project_variables = []
        self.selected_variables = set()
        self.recommendations = []
        self.data_characteristics = {}
        self.available_analysis_types = [
            'basic_statistics', 'distribution', 'correlation', 'outlier',
            'categorical', 'missing_data', 'comprehensive'
        ]
        
    def run_auto_detection(self, project_id: str):
        """Run auto-detection analysis for a project"""
        if not project_id:
            toast("Please select a project first")
            return
            
        # Set loading state
        Clock.schedule_once(lambda dt: self.screen.set_loading(True), 0)
        
        # Start analysis in background thread
        threading.Thread(
            target=self._run_auto_detection_thread,
            args=(project_id,),
            daemon=True
        ).start()
    
    def _run_auto_detection_thread(self, project_id: str):
        """Background thread for auto-detection analysis"""
        try:
            # Run auto-detection analysis
            result = self.analytics_service.run_auto_detection_analysis(project_id)
            
            Clock.schedule_once(
                lambda dt: self._handle_auto_detection_results(result), 0.1
            )
        except Exception as e:
            print(f"Error in auto-detection analysis: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error(f"Auto-detection analysis failed: {str(e)}"), 0.1
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0.1
            )
    
    def _handle_auto_detection_results(self, results):
        """Handle auto-detection analysis results"""
        try:
            if 'error' in results:
                self._show_error(results['error'])
                return
            
            # Store results
            self.current_results = results
            self.data_characteristics = results.get('data_characteristics', {})
            self.recommendations = results.get('recommendations', [])
            self.project_variables = results.get('project_variables', [])
            
            # Update screen with results
            Clock.schedule_once(
                lambda dt: self.screen.update_analysis_results(results), 0
            )
            
            # Show success message
            analyses = results.get('analyses', {})
            toast(f"Auto-detection completed: {len(analyses)} analyses run")
            
        except Exception as e:
            self._show_error(f"Failed to process auto-detection results: {str(e)}")
    
    def run_specific_analysis(self, project_id: str, analysis_type: str):
        """Run a specific type of analysis"""
        if not project_id:
            toast("Please select a project first")
            return
            
        if analysis_type not in self.available_analysis_types:
            toast(f"Unknown analysis type: {analysis_type}")
            return
        
        # Set loading state
        Clock.schedule_once(lambda dt: self.screen.set_loading(True), 0)
        
        # Start analysis in background thread
        threading.Thread(
            target=self._run_specific_analysis_thread,
            args=(project_id, analysis_type),
            daemon=True
        ).start()
    
    def _run_specific_analysis_thread(self, project_id: str, analysis_type: str):
        """Background thread for specific analysis"""
        try:
            # Map analysis types to service methods
            method_mapping = {
                'basic_statistics': 'run_basic_statistics',
                'distribution': 'run_distribution_analysis',
                'correlation': 'run_correlation_analysis',
                'outlier': 'run_outlier_analysis',
                'categorical': 'run_categorical_analysis',
                'missing_data': 'run_missing_data_analysis',
                'comprehensive': 'run_comprehensive_analysis'
            }
            
            method_name = method_mapping.get(analysis_type)
            if not method_name or not hasattr(self.analytics_service, method_name):
                raise ValueError(f"Analysis method not available: {analysis_type}")
            
            # Run the specific analysis
            method = getattr(self.analytics_service, method_name)
            result = method(project_id)
            
            Clock.schedule_once(
                lambda dt: self._handle_specific_analysis_result(analysis_type, result), 0.1
            )
            
        except Exception as e:
            print(f"Error in {analysis_type} analysis: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error(f"{analysis_type.title()} analysis failed: {str(e)}"), 0.1
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0.1
            )
    
    def _handle_specific_analysis_result(self, analysis_type: str, result: Dict):
        """Handle specific analysis result"""
        try:
            if 'error' in result:
                self._show_error(result['error'])
                return
            
            # Update current results with new analysis
            if not self.current_results:
                self.current_results = {'analyses': {}}
            
            self.current_results['analyses'][analysis_type] = result
            
            # Update screen with results
            Clock.schedule_once(
                lambda dt: self.screen.update_analysis_results(self.current_results), 0
            )
            
            # Show success message
            toast(f"{analysis_type.title()} analysis completed")
            
            # Show results dialog if available
            Clock.schedule_once(
                lambda dt: self.screen.show_results_dialog(analysis_type, result), 0.1
            )
            
        except Exception as e:
            self._show_error(f"Failed to process {analysis_type} results: {str(e)}")
    
    def run_analysis_with_selected_variables(self, project_id: str, variables: List[str]):
        """Run analysis with specific variables"""
        if not project_id:
            toast("Please select a project first")
            return
            
        if not variables:
            toast("Please select variables for analysis")
            return
        
        self.selected_variables = set(variables)
        
        # Set loading state
        Clock.schedule_once(lambda dt: self.screen.set_loading(True), 0)
        
        # Start analysis in background thread
        threading.Thread(
            target=self._run_analysis_with_variables_thread,
            args=(project_id, variables),
            daemon=True
        ).start()
    
    def _run_analysis_with_variables_thread(self, project_id: str, variables: List[str]):
        """Background thread for variable-specific analysis"""
        try:
            # Run analysis with selected variables
            result = self.analytics_service.run_variable_analysis(project_id, variables)
            
            Clock.schedule_once(
                lambda dt: self._handle_variable_analysis_result(result), 0.1
            )
            
        except Exception as e:
            print(f"Error in variable analysis: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error(f"Variable analysis failed: {str(e)}"), 0.1
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0.1
            )
    
    def _handle_variable_analysis_result(self, result: Dict):
        """Handle variable analysis result"""
        try:
            if 'error' in result:
                self._show_error(result['error'])
                return
            
            # Update current results
            if not self.current_results:
                self.current_results = {'analyses': {}}
            
            self.current_results['analyses']['variable_analysis'] = result
            
            # Update screen with results
            Clock.schedule_once(
                lambda dt: self.screen.update_analysis_results(self.current_results), 0
            )
            
            toast(f"Variable analysis completed for {len(self.selected_variables)} variables")
            
        except Exception as e:
            self._show_error(f"Failed to process variable analysis results: {str(e)}")
    
    def run_recommended_analysis(self, recommendation: Dict):
        """Run a recommended analysis"""
        try:
            recommendation_id = recommendation.get('id')
            analysis_type = recommendation.get('analysis_type', 'auto')
            project_id = recommendation.get('project_id')
            
            if not project_id and hasattr(self.screen, 'current_project_id'):
                project_id = self.screen.current_project_id
            
            if not project_id:
                toast("Project not available for recommended analysis")
                return
            
            # Run the recommended analysis
            if analysis_type == 'auto':
                self.run_auto_detection(project_id)
            else:
                self.run_specific_analysis(project_id, analysis_type)
            
            # Remove the recommendation from the list
            self.recommendations = [
                r for r in self.recommendations 
                if r.get('id') != recommendation_id
            ]
            
            # Update recommendations display
            Clock.schedule_once(
                lambda dt: self.screen.update_recommendations_display(), 0
            )
            
        except Exception as e:
            self._show_error(f"Failed to run recommended analysis: {str(e)}")
    
    def export_analytics_results(self, results: Dict):
        """Export analysis results to file"""
        try:
            if not results:
                toast("No results available for export")
                return
            
            # Prepare export data
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'project_id': getattr(self.screen, 'current_project_id', 'unknown'),
                'analysis_results': results,
                'data_characteristics': self.data_characteristics,
                'recommendations': self.recommendations,
                'selected_variables': list(self.selected_variables)
            }
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"auto_detection_results_{timestamp}.json"
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Show success message
            toast(f"Results exported to {filename}")
            Clock.schedule_once(
                lambda dt: self.screen.show_success(f"Results exported to {filename}"), 0
            )
            
        except Exception as e:
            print(f"Failed to export results: {e}")
            self._show_error(f"Export failed: {str(e)}")
    
    def get_analysis_summary(self) -> Dict:
        """Get summary of current analysis state"""
        try:
            analyses = self.current_results.get('analyses', {})
            return {
                'total_analyses': len(analyses),
                'completed_types': list(analyses.keys()),
                'has_recommendations': len(self.recommendations) > 0,
                'variables_available': len(self.project_variables),
                'variables_selected': len(self.selected_variables),
                'data_characteristics': self.data_characteristics
            }
        except Exception as e:
            print(f"Error getting analysis summary: {e}")
            return {}
    
    def clear_analysis_results(self):
        """Clear all analysis results and reset state"""
        self.current_results = {}
        self.project_variables = []
        self.selected_variables.clear()
        self.recommendations = []
        self.data_characteristics = {}
        
        # Update screen
        Clock.schedule_once(
            lambda dt: self.screen.update_analysis_results({}), 0
        )
        toast("Analysis results cleared")
    
    def get_project_variables(self, project_id: str):
        """Get available variables for a project"""
        if not project_id:
            return
            
        try:
            # Load project variables
            threading.Thread(
                target=self._load_project_variables_thread,
                args=(project_id,),
                daemon=True
            ).start()
        except Exception as e:
            self._show_error(f"Failed to load project variables: {str(e)}")
    
    def _load_project_variables_thread(self, project_id: str):
        """Background thread for loading project variables"""
        try:
            # Get project variables from analytics service
            variables = self.analytics_service.get_project_variables(project_id)
            
            Clock.schedule_once(
                lambda dt: self._handle_project_variables(variables), 0.1
            )
            
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self._show_error(f"Failed to load variables: {str(e)}"), 0.1
            )
    
    def _handle_project_variables(self, variables: List[str]):
        """Handle loaded project variables"""
        try:
            self.project_variables = variables
            
            # Update screen
            Clock.schedule_once(
                lambda dt: setattr(self.screen, 'project_variables', variables), 0
            )
            
        except Exception as e:
            self._show_error(f"Failed to process project variables: {str(e)}")
    
    def validate_analysis_request(self, project_id: str, analysis_type: str) -> bool:
        """Validate analysis request parameters"""
        try:
            if not project_id:
                toast("Project ID is required")
                return False
            
            if analysis_type not in self.available_analysis_types:
                toast(f"Unsupported analysis type: {analysis_type}")
                return False
            
            return True
            
        except Exception as e:
            self._show_error(f"Validation error: {str(e)}")
            return False
    
    def _show_error(self, error_message: str):
        """Show error message to user"""
        Clock.schedule_once(lambda dt: self.screen.set_loading(False), 0)
        Clock.schedule_once(lambda dt: self.screen.show_error(error_message), 0)
    
    def _show_success(self, message: str):
        """Show success message to user"""
        Clock.schedule_once(lambda dt: self.screen.show_success(message), 0)

    # Analytics backend methods
    def _make_analytics_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to analytics backend"""
        try:
            import requests
            base_url = "http://127.0.0.1:8001"
            url = f"{base_url}/api/v1/analytics/auto/{endpoint}"
            
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

    def run_auto_analysis_backend(self, project_id: str, analysis_type: str = "auto", 
                                target_variables: Optional[List[str]] = None) -> Dict:
        """Run comprehensive auto analysis using the analytics backend"""
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
            return {'error': f'Auto analysis failed: {str(e)}'}

    def get_data_characteristics_backend(self, project_id: str) -> Dict:
        """Get data characteristics for a project from analytics backend"""
        try:
            result = self._make_analytics_request(f'project/{project_id}/data-characteristics')
            return result
        except Exception as e:
            return {'error': f'Error getting data characteristics: {str(e)}'}

    def get_analysis_recommendations_backend(self, project_id: str) -> Dict:
        """Get smart analysis recommendations from analytics backend"""
        try:
            result = self._make_analytics_request(f'project/{project_id}/recommendations')
            return result
        except Exception as e:
            return {'error': f'Error getting analysis recommendations: {str(e)}'}

    def get_project_stats_backend(self, project_id: str) -> Dict:
        """Get basic project statistics from analytics backend"""
        try:
            result = self._make_analytics_request(f"project/{project_id}/stats")
            return result
        except Exception as e:
            return {'error': f'Error getting project stats: {str(e)}'}