"""
Categorical Analytics Handler
Specialized service for categorical data analysis and chi-square tests
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


class CategoricalAnalyticsHandler:
    """Handler for categorical analysis operations"""
    
    def __init__(self, analytics_service, analytics_screen):
        self.analytics_service = analytics_service
        self.analytics_screen = analytics_screen
        self.selected_variables = []
        self.analysis_dialog = None
    
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
                lambda dt: self._display_categorical_results(results), 0
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
    
    def _display_categorical_results(self, results):
        """Display categorical analysis results"""
        print(f"[DEBUG] Categorical results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                toast("Backend connection error")
            else:
                toast(f"Analysis Error: {error_msg}")
            return
        
        # Show results in dialog
        self._show_categorical_results_dialog(results)
    
    def _show_categorical_results_dialog(self, results: Dict):
        """Show categorical analysis results in a dialog"""
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
            summary_card = self._create_categorical_summary_card(summary)
            results_layout.add_widget(summary_card)
        
        # Individual variable analysis
        if 'results' in results and 'categorical_analysis' in results['results']:
            categorical_data = results['results']['categorical_analysis']
            
            for variable, analysis in categorical_data.items():
                if 'error' not in analysis:
                    var_card = self._create_variable_categorical_card(variable, analysis)
                    results_layout.add_widget(var_card)
        
        # Cross-tabulation results
        if 'results' in results and 'cross_tabulations' in results['results']:
            cross_tabs = results['results']['cross_tabulations']
            if cross_tabs:
                cross_tab_card = self._create_cross_tabulation_card(cross_tabs)
                results_layout.add_widget(cross_tab_card)
        
        results_content.add_widget(results_layout)
        
        # Create results dialog
        results_dialog = MDDialog(
            title="Categorical Analysis Results",
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
    
    def _create_categorical_summary_card(self, summary: Dict) -> MDCard:
        """Create summary card for categorical analysis"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(160),
            elevation=2,
            md_bg_color=(0.98, 1.0, 0.99, 1),
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
            icon="chart-pie",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.8, 0.6, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(32)
        )
        
        header_label = MDLabel(
            text="Categorical Analysis Summary",
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
Cross-tabulations: {summary.get('cross_tabs_computed', 'N/A')}
Analysis Methods: Frequency analysis, chi-square tests, Cramer's V"""
        
        summary_label = MDLabel(
            text=summary_text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(100)
        )
        card.add_widget(summary_label)
        
        return card
    
    def _create_variable_categorical_card(self, variable: str, analysis: Dict) -> MDCard:
        """Create card for individual variable categorical analysis"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(260),
            elevation=2,
            md_bg_color=(0.99, 0.98, 1.0, 1),
            radius=[8, 8, 8, 8]
        )
        
        # Variable header
        header_label = MDLabel(
            text=f"🏷️ {variable}",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32),
            bold=True
        )
        card.add_widget(header_label)
        
        # Categorical analysis results
        unique_count = analysis.get('unique', 'N/A')
        most_common = analysis.get('top', 'N/A')
        most_common_freq = analysis.get('freq', 'N/A')
        missing_count = analysis.get('missing', 0)
        
        # Create info grid
        info_grid = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(100)
        )
        
        # Category info
        unique_info = self._create_categorical_info_item("Unique Values", str(unique_count))
        common_info = self._create_categorical_info_item("Most Common", str(most_common))
        freq_info = self._create_categorical_info_item("Frequency", str(most_common_freq))
        missing_info = self._create_categorical_info_item("Missing", str(missing_count))
        
        info_grid.add_widget(unique_info)
        info_grid.add_widget(common_info)
        info_grid.add_widget(freq_info)
        info_grid.add_widget(missing_info)
        
        card.add_widget(info_grid)
        
        # Category distribution
        if 'value_counts' in analysis:
            value_counts = analysis['value_counts']
            dist_label = MDLabel(
                text="Category Distribution:",
                font_style="Subtitle2",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(dist_label)
            
            # Show top categories
            categories_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(4),
                size_hint_y=None,
                height=dp(60)
            )
            
            # Sort categories by frequency and show top 3
            sorted_categories = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
            for cat, count in sorted_categories[:3]:
                cat_text = f"• {cat}: {count}"
                cat_label = MDLabel(
                    text=cat_text,
                    font_style="Caption",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(16)
                )
                categories_layout.add_widget(cat_label)
            
            card.add_widget(categories_layout)
        
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
        
        charts_btn = MDFlatButton(
            text="View Distribution",
            size_hint_x=1,
            on_release=lambda x: self._show_distribution_details(variable, analysis)
        )
        
        action_layout.add_widget(details_btn)
        action_layout.add_widget(charts_btn)
        card.add_widget(action_layout)
        
        return card
    
    def _create_cross_tabulation_card(self, cross_tabs: Dict) -> MDCard:
        """Create card for cross-tabulation results"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(300),
            elevation=2,
            md_bg_color=(1.0, 0.99, 0.98, 1),
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
            icon="table",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.4, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(32)
        )
        
        header_label = MDLabel(
            text="Cross-Tabulation Analysis",
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(header_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Cross-tabulation results
        scroll_view = MDScrollView(
            size_hint_y=1
        )
        
        cross_tabs_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True
        )
        
        for cross_tab_name, cross_tab_data in cross_tabs.items():
            if 'error' not in cross_tab_data:
                cross_tab_item = self._create_cross_tab_item(cross_tab_name, cross_tab_data)
                cross_tabs_layout.add_widget(cross_tab_item)
        
        scroll_view.add_widget(cross_tabs_layout)
        card.add_widget(scroll_view)
        
        return card
    
    def _create_cross_tab_item(self, cross_tab_name: str, cross_tab_data: Dict) -> MDBoxLayout:
        """Create a cross-tabulation item"""
        item_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(100),
            md_bg_color=(1, 1, 1, 0.6),
            radius=6,
            padding=dp(12)
        )
        
        # Cross-tab name
        name_label = MDLabel(
            text=cross_tab_name.replace('_vs_', ' vs ').title(),
            font_style="Subtitle2",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(24),
            bold=True
        )
        item_layout.add_widget(name_label)
        
        # Chi-square test results
        chi_square = cross_tab_data.get('chi_square_test', {})
        cramers_v = cross_tab_data.get('cramers_v', 'N/A')
        
        stats_text = f"""Chi-square: {chi_square.get('statistic', 'N/A'):.3f}
P-value: {chi_square.get('p_value', 'N/A'):.4f}
Cramer's V: {cramers_v:.3f}"""
        
        stats_label = MDLabel(
            text=stats_text,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(60)
        )
        item_layout.add_widget(stats_label)
        
        return item_layout
    
    def _create_categorical_info_item(self, label: str, value: str) -> MDBoxLayout:
        """Create a categorical info item"""
        item_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(40),
            md_bg_color=(1, 1, 1, 0.6),
            radius=6,
            padding=dp(8)
        )
        
        label_widget = MDLabel(
            text=label,
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(14)
        )
        
        value_widget = MDLabel(
            text=str(value),
            font_style="Body2",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(20),
            bold=True
        )
        
        item_layout.add_widget(label_widget)
        item_layout.add_widget(value_widget)
        
        return item_layout
    
    def _show_variable_details(self, variable: str, analysis: Dict):
        """Show detailed analysis for a categorical variable"""
        details_text = f"Detailed Analysis for {variable}\n\n"
        
        # Basic statistics
        details_text += "Basic Statistics:\n"
        details_text += f"• Unique Values: {analysis.get('unique', 'N/A')}\n"
        details_text += f"• Most Common: {analysis.get('top', 'N/A')}\n"
        details_text += f"• Frequency: {analysis.get('freq', 'N/A')}\n"
        details_text += f"• Missing Values: {analysis.get('missing', 'N/A')}\n\n"
        
        # Value counts
        if 'value_counts' in analysis:
            value_counts = analysis['value_counts']
            details_text += "Value Distribution:\n"
            
            # Sort by frequency
            sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
            for value, count in sorted_values[:10]:  # Show top 10
                percentage = (count / sum(value_counts.values())) * 100
                details_text += f"• {value}: {count} ({percentage:.1f}%)\n"
            
            if len(sorted_values) > 10:
                details_text += f"... and {len(sorted_values) - 10} more categories\n"
        
        # Show in dialog
        self._show_text_dialog(f"Details: {variable}", details_text)
    
    def _show_distribution_details(self, variable: str, analysis: Dict):
        """Show distribution details for a categorical variable"""
        if 'value_counts' not in analysis:
            toast("No distribution data available")
            return
        
        value_counts = analysis['value_counts']
        
        details_text = f"Distribution for {variable}\n\n"
        details_text += f"Total Categories: {len(value_counts)}\n"
        details_text += f"Total Observations: {sum(value_counts.values())}\n\n"
        
        details_text += "Category Frequencies:\n"
        sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        
        for value, count in sorted_values:
            percentage = (count / sum(value_counts.values())) * 100
            details_text += f"{value}: {count} ({percentage:.1f}%)\n"
        
        # Show in dialog
        self._show_text_dialog(f"Distribution: {variable}", details_text)
    
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
            ("correlation", "🔗 Correlation Analysis", "Variable relationships"),
            ("outlier", "🎯 Outlier Detection", "Find unusual values"),
            ("quality", "🔍 Data Quality Check", "Assess data completeness"),
            ("distribution", "📈 Distribution Analysis", "If variables are numeric"),
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
        
        if analysis_type == "correlation":
            self.analytics_service.run_analysis(project_id, "correlation")
        elif analysis_type == "outlier":
            self.analytics_service.run_outlier_analysis(project_id)
        elif analysis_type == "quality":
            self.analytics_service.run_data_quality_analysis(project_id)
        elif analysis_type == "distribution":
            self.analytics_service.run_distribution_analysis(project_id)
    
    def _export_results(self, results: Dict):
        """Export categorical analysis results"""
        try:
            exported = self.analytics_service.export_analysis_results(results, 'json')
            toast("Categorical analysis results exported")
        except Exception as e:
            toast(f"Export failed: {str(e)}")
    
    def show_variable_selection_for_categorical(self, project_id: str):
        """Show variable selection dialog specifically for categorical analysis"""
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
                lambda dt: self._show_categorical_variable_dialog(variables), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: toast("Error loading variables"), 0
            )
    
    def _show_categorical_variable_dialog(self, variables: Dict):
        """Show variable selection dialog for categorical analysis"""
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
            text="Select categorical variables for analysis:",
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
        
        # Show categorical variables for analysis
        categorical_vars = variables.get('categorical_variables', [])
        
        if not categorical_vars:
            no_vars_label = MDLabel(
                text="No categorical variables found for analysis",
                font_style="Body1",
                theme_text_color="Hint",
                halign="center"
            )
            variables_layout.add_widget(no_vars_label)
        else:
            for var in categorical_vars:
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
            title="Categorical Analysis - Variable Selection",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.8, 0.7),
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: self.analysis_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Run Categorical Analysis",
                    on_release=lambda x: self._run_categorical_with_selected_vars()
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
    
    def _run_categorical_with_selected_vars(self):
        """Run categorical analysis with selected variables"""
        if self.analysis_dialog:
            self.analysis_dialog.dismiss()
        
        if not self.selected_variables:
            toast("Please select at least one variable")
            return
        
        project_id = self.analytics_screen.current_project_id
        if not project_id:
            toast("No project selected")
            return
        
        toast(f"Running categorical analysis on {len(self.selected_variables)} variables...")
        self.run_categorical_analysis(project_id, self.selected_variables) 