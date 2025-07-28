"""
Categorical Analytics Handler
Specialized service for categorical data analysis and chi-square tests
"""

from typing import Dict, List, Any, Optional
import threading
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class CategoricalAnalyticsHandler:
    """Handler for categorical analysis operations - Business Logic Only"""
    
    def __init__(self, analytics_service, analytics_screen):
        self.analytics_service = analytics_service
        self.analytics_screen = analytics_screen
        self.selected_variables = []
    
    def run_categorical_analysis(self, project_id: str, variables: Optional[List[str]] = None):
        """Run categorical analysis for selected variables"""
        if not project_id:
            return
            
        self.analytics_screen.set_loading(True)
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
                lambda dt: self.analytics_screen.set_loading(False), 0
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
        
        # Delegate to analytics screen to handle UI display
        self.analytics_screen.display_categorical_results(results)
    
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
        if not self.analytics_screen.current_project_id:
            toast("Please select a project first")
            return
        
        # Delegate to analytics screen to handle UI and run analysis
        self.analytics_screen.run_categorical_additional_analysis(analysis_type)
    
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
        self.analytics_screen.show_categorical_variable_selection_ui(project_id)
    
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
        self.analytics_screen.show_categorical_variable_selection(categorical_vars)
    
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
        
        if not self.analytics_screen.current_project_id:
            toast("Please select a project first")
            return
        
        self.run_categorical_analysis(
            self.analytics_screen.current_project_id, 
            self.selected_variables
        ) 