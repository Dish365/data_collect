"""
Distribution Analytics Handler
Specialized service for distribution analysis and statistical testing
"""

from typing import Dict, List, Any, Optional
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
import threading
from kivy.clock import Clock
from kivymd.toast import toast


class DistributionAnalyticsHandler:
    """Handler for distribution analysis operations"""
    
    def __init__(self, analytics_service, analytics_screen):
        self.analytics_service = analytics_service
        self.analytics_screen = analytics_screen
        self.selected_variables = []
        self.analysis_dialog = None
    
    def run_distribution_analysis(self, project_id: str, variables: Optional[List[str]] = None):
        """Run distribution analysis for selected variables"""
        if not project_id:
            return
            
        self.analytics_screen.set_loading(True)
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
                lambda dt: self._display_distribution_results(results), 0
            )
        except Exception as e:
            print(f"Error in distribution analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Distribution analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _display_distribution_results(self, results):
        """Display distribution analysis results"""
        print(f"[DEBUG] Distribution results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                toast("Backend connection error")
            else:
                toast(f"Analysis Error: {error_msg}")
            return
        
        # Show results in dialog
        self._show_distribution_results_dialog(results)
    
    def _show_distribution_results_dialog(self, results: Dict):
        """Show distribution analysis results in a dialog"""
        # Create scrollable results content
        results_content = MDScrollView(
            size_hint=(1, 1)
        )
        
        results_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            adaptive_height=True,
            padding=dp(16)
        )
        
        # Results summary
        if 'results' in results and 'summary' in results['results']:
            summary = results['results']['summary']
            summary_card = self._create_distribution_summary_card(summary)
            results_layout.add_widget(summary_card)
        
        # Distribution analysis details
        if 'results' in results and 'distribution_analysis' in results['results']:
            distribution_data = results['results']['distribution_analysis']
            
            for variable, analysis in distribution_data.items():
                if 'error' not in analysis:
                    var_card = self._create_variable_distribution_card(variable, analysis)
                    results_layout.add_widget(var_card)
        
        results_content.add_widget(results_layout)
        
        # Create results dialog
        results_dialog = MDDialog(
            title="Distribution Analysis Results",
            type="custom",
            content_cls=results_content,
            size_hint=(0.95, 0.85),
            buttons=[
                MDFlatButton(
                    text="Close",
                    on_release=lambda x: results_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Export Results",
                    on_release=lambda x: self._export_results(results)
                ),
                MDRaisedButton(
                    text="Run More Analysis",
                    on_release=lambda x: self._show_additional_analysis_options(results_dialog)
                )
            ]
        )
        
        results_dialog.open()
    
    def _create_distribution_summary_card(self, summary: Dict) -> MDCard:
        """Create summary card for distribution analysis"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(140),
            elevation=2,
            md_bg_color=(0.98, 0.99, 1.0, 1),
            radius=[8, 8, 8, 8]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32)
        )
        
        header_icon = MDIconButton(
            icon="chart-histogram",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(32)
        )
        
        header_label = MDLabel(
            text="Distribution Analysis Summary",
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(header_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Summary stats
        summary_text = f"""Variables Analyzed: {summary.get('variables_analyzed', 'N/A')}
Observations: {summary.get('observations', 'N/A'):,}
Analysis Methods: Normality tests, skewness, kurtosis, outlier detection"""
        
        summary_label = MDLabel(
            text=summary_text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(80)
        )
        card.add_widget(summary_label)
        
        return card
    
    def _create_variable_distribution_card(self, variable: str, analysis: Dict) -> MDCard:
        """Create card for individual variable distribution analysis"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(280),
            elevation=2,
            md_bg_color=(0.99, 1.0, 0.98, 1),
            radius=[8, 8, 8, 8]
        )
        
        # Variable header
        header_label = MDLabel(
            text=f"📊 {variable}",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32),
            bold=True
        )
        card.add_widget(header_label)
        
        # Distribution analysis results
        dist_analysis = analysis.get('distribution_analysis', {})
        normality_test = analysis.get('normality_test', {})
        skew_kurt = analysis.get('skewness_kurtosis', {})
        outliers = analysis.get('outliers', {})
        
        # Create info grid
        info_grid = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(120)
        )
        
        # Distribution info
        dist_info = self._create_distribution_info_item("Distribution Type", 
                                                       dist_analysis.get('likely_distribution', 'Unknown'))
        normality_info = self._create_distribution_info_item("Normality Test", 
                                                            f"p-value: {normality_test.get('p_value', 'N/A')}")
        skewness_info = self._create_distribution_info_item("Skewness", 
                                                           f"{skew_kurt.get('skewness', 'N/A'):.3f}")
        kurtosis_info = self._create_distribution_info_item("Kurtosis", 
                                                           f"{skew_kurt.get('kurtosis', 'N/A'):.3f}")
        
        info_grid.add_widget(dist_info)
        info_grid.add_widget(normality_info)
        info_grid.add_widget(skewness_info)
        info_grid.add_widget(kurtosis_info)
        
        card.add_widget(info_grid)
        
        # Outliers information
        outlier_count = len(outliers.get('outlier_indices', []))
        outlier_percentage = outliers.get('outlier_percentage', 0)
        
        outlier_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40)
        )
        
        outlier_icon = MDIconButton(
            icon="target",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.4, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(32)
        )
        
        outlier_label = MDLabel(
            text=f"Outliers: {outlier_count} ({outlier_percentage:.1f}%)",
            font_style="Body1",
            theme_text_color="Secondary"
        )
        
        outlier_layout.add_widget(outlier_icon)
        outlier_layout.add_widget(outlier_label)
        card.add_widget(outlier_layout)
        
        # Action buttons
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(36)
        )
        
        details_btn = MDFlatButton(
            text="View Details",
            size_hint_x=1,
            on_release=lambda x: self._show_variable_details(variable, analysis)
        )
        
        outliers_btn = MDFlatButton(
            text="View Outliers",
            size_hint_x=1,
            on_release=lambda x: self._show_outliers_details(variable, outliers)
        )
        
        action_layout.add_widget(details_btn)
        action_layout.add_widget(outliers_btn)
        card.add_widget(action_layout)
        
        return card
    
    def _create_distribution_info_item(self, label: str, value: str) -> MDBoxLayout:
        """Create a distribution info item"""
        item_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(1, 1, 1, 0.6),
            radius=6,
            padding=dp(8)
        )
        
        label_widget = MDLabel(
            text=label,
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(16)
        )
        
        value_widget = MDLabel(
            text=str(value),
            font_style="Body1",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(24),
            bold=True
        )
        
        item_layout.add_widget(label_widget)
        item_layout.add_widget(value_widget)
        
        return item_layout
    
    def _show_variable_details(self, variable: str, analysis: Dict):
        """Show detailed analysis for a variable"""
        # Format detailed analysis information
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
        
        # Show in dialog
        self._show_text_dialog(f"Details: {variable}", details_text)
    
    def _show_outliers_details(self, variable: str, outliers: Dict):
        """Show outliers details for a variable"""
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
        
        # Show in dialog
        self._show_text_dialog(f"Outliers: {variable}", details_text)
    
    def _show_text_dialog(self, title: str, text: str):
        """Show text information in a dialog"""
        content = MDScrollView()
        
        content_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True,
            padding=dp(16)
        )
        
        text_label = MDLabel(
            text=text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            adaptive_height=True,
            text_size=(dp(400), None)
        )
        
        content_layout.add_widget(text_label)
        content.add_widget(content_layout)
        
        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
            size_hint=(0.8, 0.7),
            buttons=[
                MDFlatButton(
                    text="Close",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        
        dialog.open()
    
    def _show_additional_analysis_options(self, parent_dialog):
        """Show additional analysis options"""
        # Close parent dialog first
        parent_dialog.dismiss()
        
        # Show options for related analyses
        options = [
            ("outlier", "🎯 Detailed Outlier Analysis", "Advanced outlier detection methods"),
            ("categorical", "🏷️ Categorical Analysis", "If variables have categories"),
            ("correlation", "🔗 Correlation Analysis", "Variable relationships"),
            ("quality", "🔍 Data Quality Check", "Assess data completeness"),
        ]
        
        # Create options menu
        menu_items = []
        for option_code, title, description in options:
            menu_items.append({
                "text": f"{title}\n{description}",
                "viewclass": "TwoLineListItem",
                "on_release": lambda x=option_code: self._run_additional_analysis(x)
            })
        
        from kivymd.uix.menu import MDDropdownMenu
        analysis_menu = MDDropdownMenu(
            caller=self.analytics_screen.ids.auto_detection_content,
            items=menu_items,
            width_mult=5,
            position="center"
        )
        
        analysis_menu.open()
    
    def _run_additional_analysis(self, analysis_type: str):
        """Run additional analysis type"""
        project_id = self.analytics_screen.current_project_id
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
    
    def _export_results(self, results: Dict):
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
                lambda dt: self._show_distribution_variable_dialog(variables), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: toast("Error loading variables"), 0
            )
    
    def _show_distribution_variable_dialog(self, variables: Dict):
        """Show variable selection dialog for distribution analysis"""
        if 'error' in variables:
            toast("Error loading project variables")
            return
        
        # Create dialog content
        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(400),
            adaptive_height=True
        )
        
        # Instructions
        instructions = MDLabel(
            text="Select numeric variables for distribution analysis:",
            font_style="Subtitle1",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32)
        )
        dialog_content.add_widget(instructions)
        
        # Variable selection
        scroll_view = MDScrollView(size_hint=(1, 1))
        
        variables_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True
        )
        
        self.selected_variables = []
        
        # Only show numeric variables for distribution analysis
        numeric_vars = variables.get('numeric_variables', [])
        
        if not numeric_vars:
            no_vars_label = MDLabel(
                text="No numeric variables found for distribution analysis",
                font_style="Body1",
                theme_text_color="Hint",
                halign="center"
            )
            variables_layout.add_widget(no_vars_label)
        else:
            for var in numeric_vars:
                var_layout = MDBoxLayout(
                    orientation="horizontal",
                    spacing=dp(8),
                    size_hint_y=None,
                    height=dp(32)
                )
                
                checkbox = MDCheckbox(
                    size_hint_x=None,
                    width=dp(32),
                    active=True  # Default to selected
                )
                checkbox.bind(active=lambda cb, active, v=var: self._update_variable_selection(v, active))
                
                var_label = MDLabel(
                    text=var,
                    font_style="Body1",
                    theme_text_color="Secondary"
                )
                
                var_layout.add_widget(checkbox)
                var_layout.add_widget(var_label)
                variables_layout.add_widget(var_layout)
                
                # Default to all selected
                if var not in self.selected_variables:
                    self.selected_variables.append(var)
        
        scroll_view.add_widget(variables_layout)
        dialog_content.add_widget(scroll_view)
        
        # Create dialog
        self.analysis_dialog = MDDialog(
            title="Distribution Analysis - Variable Selection",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.8, 0.7),
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: self.analysis_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Run Distribution Analysis",
                    on_release=lambda x: self._run_distribution_with_selected_vars()
                )
            ]
        )
        
        self.analysis_dialog.open()
    
    def _update_variable_selection(self, variable: str, active: bool):
        """Update selected variables list"""
        if active and variable not in self.selected_variables:
            self.selected_variables.append(variable)
        elif not active and variable in self.selected_variables:
            self.selected_variables.remove(variable)
    
    def _run_distribution_with_selected_vars(self):
        """Run distribution analysis with selected variables"""
        if self.analysis_dialog:
            self.analysis_dialog.dismiss()
        
        if not self.selected_variables:
            toast("Please select at least one variable")
            return
        
        project_id = self.analytics_screen.current_project_id
        if not project_id:
            toast("No project selected")
            return
        
        toast(f"Running distribution analysis on {len(self.selected_variables)} variables...")
        self.run_distribution_analysis(project_id, self.selected_variables) 