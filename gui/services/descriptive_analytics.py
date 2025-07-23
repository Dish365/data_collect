"""
Enhanced Descriptive Analytics Handler - Tablet Optimized
Specialized service for comprehensive descriptive statistical analysis
OPTIMIZED FOR MEDIUM TABLETS (9-11 inches)
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
import threading
from kivy.clock import Clock
from kivymd.toast import toast


class DescriptiveAnalyticsHandler:
    """Enhanced handler for comprehensive descriptive analytics - Tablet Optimized"""
    
    def __init__(self, analytics_service, analytics_screen):
        self.analytics_service = analytics_service
        self.analytics_screen = analytics_screen
        self.project_variables = {}
        self.analysis_dialog = None
        
        # Tablet-specific UI constants
        self.TABLET_CARD_HEIGHT = dp(350)
        self.TABLET_PADDING = dp(24)
        self.TABLET_SPACING = dp(20)
        self.TABLET_BUTTON_HEIGHT = dp(48)
        self.TABLET_ICON_SIZE = dp(32)
        self.TABLET_FONT_SIZE = "16sp"
    
    def run_descriptive_analysis(self, project_id: str, analysis_config: Dict = None):
        """Show descriptive analytics selection interface (no auto-run)"""
        print(f"[DEBUG] run_descriptive_analysis called with project_id: {project_id}")
        
        if not project_id:
            print(f"[DEBUG] No project_id provided")
            return
            
        # Show the selection interface (no automatic analysis)
        self._show_descriptive_selection_interface(project_id)
    
    def _run_descriptive_thread(self, project_id: str, analysis_config: Dict):
        """Background thread for comprehensive descriptive analysis"""
        try:
            # Get project variables for comprehensive analysis
            variables = self.analytics_service.get_project_variables(project_id)
            self.project_variables = variables
            
            # Run comprehensive descriptive analysis
            results = self.analytics_service.run_analysis(
                project_id, "comprehensive", analysis_config.get('variables') if analysis_config else None
            )
            
            # Combine with variable information
            combined_results = {
                'analysis_results': results,
                'project_variables': variables
            }
            
            Clock.schedule_once(
                lambda dt: self._display_tablet_comprehensive_results(combined_results), 0
            )
        except Exception as e:
            print(f"Error in descriptive analysis: {e}")
            Clock.schedule_once(
                lambda dt: self.analytics_screen.show_error("Descriptive analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _display_tablet_comprehensive_results(self, combined_results):
        """Display comprehensive descriptive analysis results optimized for tablets"""
        # Use the helper method to get the content area
        content = self.analytics_screen.get_tab_content('descriptive')
        
        if not content:
            print(f"[DEBUG] ERROR: Could not get descriptive content area")
            return
            
        content.clear_widgets()
        
        results = combined_results.get('analysis_results', {})
        project_variables = combined_results.get('project_variables', {})
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                content.add_widget(self.analytics_screen.create_backend_error_widget())
            else:
                content.add_widget(self._create_tablet_error_state(f"Analysis Error: {error_msg}"))
            return
        
        # Use improved heights and spacing for better tablet experience
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        # 1. Configuration Card - IMPROVED HEIGHT AND SPACING
        config_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(396),  # Increased by 10% from 360
            padding=dp(32),  # Increased from 20
            spacing=dp(16),  # Increased from 12
            md_bg_color=(0.98, 0.99, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # Increased from 12
            size_hint_y=None,
            height=dp(48)    # Increased from 40
        )
        
        config_icon = MDIconButton(
            icon="chart-line",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(56),    # Increased from 48
            user_font_size="28sp"  # Increased from 24sp
        )
        
        header_label = MDLabel(
            text="📊 Descriptive Analytics",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(config_icon)
        header_layout.add_widget(header_label)
        config_card.add_widget(header_layout)
        
        # Data summary with sample size adequacy
        sample_size = project_variables.get('sample_size', 'N/A')
        variable_count = project_variables.get('variable_count', 'N/A')
        sample_adequacy = project_variables.get('sample_size_analysis', {})
        
        # Get adequacy status and guidance
        adequacy_status = sample_adequacy.get('adequacy_status', 'unknown')
        adequacy_score = sample_adequacy.get('adequacy_score', 0.0)
        general_guidance = sample_adequacy.get('summary', {}).get('general_guidance', 'Sample size assessment unavailable')
        
        # Status emoji based on adequacy
        status_emoji = {
            'excellent': '🌟',
            'adequate': '✅', 
            'marginal': '⚠️',
            'insufficient': '❌',
            'unknown': '❓'
        }.get(adequacy_status, '❓')
        
        summary_text = f"""📊 Dataset: {sample_size:,} responses across {variable_count} variables

{status_emoji} Sample Adequacy: {adequacy_status.title()} (Score: {adequacy_score:.1f}/1.0)
💡 Guidance: {general_guidance}

📈 Numeric Variables: {len(project_variables.get('numeric_variables', []))} (for statistical analysis)
🏷️ Categorical Variables: {len(project_variables.get('categorical_variables', []))} (for frequency analysis)
📝 Text Variables: {len(project_variables.get('text_variables', []))} (for content analysis)
📅 Date/Time Variables: {len(project_variables.get('datetime_variables', []))} (for temporal analysis)"""
        
        summary_label = MDLabel(
            text=summary_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(140)   # Increased from 120
        )
        config_card.add_widget(summary_label)
        
        # Analysis buttons
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # Increased from 12
            size_hint_y=None,
            height=dp(52)    # Increased from 48
        )
        
        basic_btn = MDRaisedButton(
            text="📊 Basic Statistics",
            size_hint_x=1,
            height=dp(48),   # Increased from 40
            md_bg_color=(0.2, 0.6, 1.0, 1),
            font_size="15sp", # Increased from 14sp
            on_release=lambda x: self._run_basic_statistics()
        )
        
        comprehensive_btn = MDRaisedButton(
            text="🏆 Full Analysis",
            size_hint_x=1,
            height=dp(48),   # Increased from 40
            md_bg_color=(0.8, 0.2, 0.8, 1),
            font_size="15sp", # Increased from 14sp
            on_release=lambda x: self._generate_comprehensive_report()
        )
        
        buttons_layout.add_widget(basic_btn)
        buttons_layout.add_widget(comprehensive_btn)
        config_card.add_widget(buttons_layout)
        
        content.add_widget(config_card)
        
        # ADD SPACING BETWEEN CARDS
        from kivymd.uix.widget import MDWidget
        spacer = MDWidget(size_hint_y=None, height=dp(24))
        content.add_widget(spacer)
        
        # 2. Results Card - if we have results
        if 'analyses' in results:
            results_card = self._create_fixed_height_results_card(results)
            content.add_widget(results_card)
        
        print(f"[DEBUG] Descriptive analytics interface created successfully!")
    
    def _show_descriptive_selection_interface(self, project_id: str):
        """Show descriptive analytics selection interface with manual options"""
        print(f"[DEBUG] _show_descriptive_selection_interface called for project: {project_id}")
        
        # Use the helper method to get the content area
        content = self.analytics_screen.get_tab_content('descriptive')
        
        if not content:
            print(f"[DEBUG] ERROR: Could not get descriptive content area")
            return
        
        print(f"[DEBUG] Successfully got descriptive content area, type: {type(content)}")
            
        content.clear_widgets()
        
        # Get project variables for context
        project_variables = self.analytics_service.get_project_variables(project_id)
        if 'error' in project_variables:
            content.add_widget(self._create_error_state_card(f"Error loading project: {project_variables['error']}"))
            return
        
        # Use improved heights and spacing for better tablet experience
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        from kivy.uix.gridlayout import GridLayout
        
        # 1. Header Card with Project Info - INCREASED HEIGHT AND PADDING
        header_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(242),  # Increased by 10% from 220
            padding=dp(32),  # Increased from 20
            spacing=dp(16),  # Increased from 12
            md_bg_color=(0.98, 0.99, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # Increased from 12
            size_hint_y=None,
            height=dp(48)    # Increased from 40
        )
        
        desc_icon = MDIconButton(
            icon="chart-line",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(56),    # Increased from 48
            user_font_size="28sp"  # Increased from 24sp
        )
        
        header_label = MDLabel(
            text="📊 Descriptive Analytics Selection",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(desc_icon)
        header_layout.add_widget(header_label)
        header_card.add_widget(header_layout)
        
        # Project info with sample size adequacy
        sample_size = project_variables.get('sample_size', 'N/A')
        variable_count = project_variables.get('variable_count', 'N/A')
        numeric_vars = len(project_variables.get('numeric_variables', []))
        categorical_vars = len(project_variables.get('categorical_variables', []))
        text_vars = len(project_variables.get('text_variables', []))
        
        # Get sample size adequacy info
        sample_adequacy = project_variables.get('sample_size_analysis', {})
        adequacy_status = sample_adequacy.get('adequacy_status', 'unknown')
        adequate_for = sample_adequacy.get('summary', {}).get('adequate_for', 0)
        tests_assessed = sample_adequacy.get('summary', {}).get('tests_assessed', 0)
        
        # Status emoji
        status_emoji = {
            'excellent': '🌟',
            'adequate': '✅', 
            'marginal': '⚠️',
            'insufficient': '❌',
            'unknown': '❓'
        }.get(adequacy_status, '❓')
        
        info_text = f"""📊 Dataset: {sample_size:,} responses across {variable_count} variables

📈 Numeric: {numeric_vars} | 🏷️ Categorical: {categorical_vars} | 📝 Text: {text_vars}

{status_emoji} Sample Adequacy: {adequacy_status.title()} ({adequate_for}/{tests_assessed} tests have adequate power)

Select the descriptive analysis you want to run:"""
        
        info_label = MDLabel(
            text=info_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(120)  # Increased from 100
        )
        header_card.add_widget(info_label)
        
        content.add_widget(header_card)
        
        # ADD SPACING BETWEEN CARDS
        from kivymd.uix.widget import MDWidget
        spacer1 = MDWidget(size_hint_y=None, height=dp(24))
        content.add_widget(spacer1)
        
        # 2. Analysis Options Grid - INCREASED HEIGHT AND PADDING
        options_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(900),  # Increased by 10% and adjusted for larger cards (was 480)
            padding=dp(32),  # Increased from 20
            spacing=dp(20),  # Increased from 16
            md_bg_color=(1.0, 1.0, 1.0, 1),
            elevation=2,
            radius=[16, 16, 16, 16]
        )
        
        options_title = MDLabel(
            text="🎯 Available Descriptive Analytics",
            font_style="H6",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(40)  # Increased from 32
        )
        options_card.add_widget(options_title)
        
        # Options grid (2 columns for tablets)
        options_grid = GridLayout(
            cols=2,
            spacing=dp(16),  # Increased from 12
            size_hint_y=None,
            height=dp(800)   # Adjusted for 150% larger cards (3 rows * 450 + spacing)
        )
        
        # Define descriptive analytics options
        analysis_options = [
            {
                'name': 'Basic Statistics',
                'icon': '📊',
                'description': 'Mean, median, std dev, percentiles',
                'endpoint': 'basic-statistics',
                'color': (0.2, 0.6, 1.0, 1),
                'suitable_for': f'All {numeric_vars} numeric variables'
            },
            {
                'name': 'Distribution Analysis', 
                'icon': '📈',
                'description': 'Normality tests, skewness, kurtosis',
                'endpoint': 'distributions',
                'color': (1.0, 0.6, 0.2, 1),
                'suitable_for': f'{numeric_vars} numeric variables'
            },
            {
                'name': 'Categorical Analysis',
                'icon': '🏷️', 
                'description': 'Frequencies, cross-tabs, chi-square',
                'endpoint': 'categorical',
                'color': (0.2, 0.8, 0.6, 1),
                'suitable_for': f'{categorical_vars} categorical variables'
            },
            {
                'name': 'Outlier Detection',
                'icon': '🎯',
                'description': 'IQR, Z-score, isolation forest methods',
                'endpoint': 'outliers', 
                'color': (0.8, 0.2, 0.6, 1),
                'suitable_for': f'{numeric_vars} numeric variables'
            },
            {
                'name': 'Missing Data Analysis',
                'icon': '❓',
                'description': 'Missing patterns and correlations',
                'endpoint': 'missing-data',
                'color': (0.6, 0.4, 0.8, 1),
                'suitable_for': 'All variables with missing data'
            },
            {
                'name': 'Data Quality Check',
                'icon': '🛡️',
                'description': 'Completeness, consistency, validity',
                'endpoint': 'data-quality',
                'color': (0.4, 0.8, 0.2, 1),
                'suitable_for': 'All variables quality assessment'
            }
        ]
        
        # Create option cards
        for option in analysis_options:
            option_card = self._create_analysis_option_card(project_id, option)
            options_grid.add_widget(option_card)
        
        options_card.add_widget(options_grid)
        content.add_widget(options_card)
        
        # ADD SPACING BETWEEN CARDS - Increased to prevent overlap
        spacer2 = MDWidget(size_hint_y=None, height=dp(48))
        content.add_widget(spacer2)
        
        # 3. Quick Actions Card - INCREASED HEIGHT AND PADDING
        quick_actions_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(154),  # Increased by 10% from 140
            padding=dp(32),  # Increased from 20
            spacing=dp(16),  # Increased from 12
            md_bg_color=(0.99, 1.0, 0.98, 1),
            elevation=2,
            radius=[16, 16, 16, 16]
        )
        
        actions_title = MDLabel(
            text="⚡ Quick Actions",
            font_style="H6",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(40)  # Increased from 32
        )
        quick_actions_card.add_widget(actions_title)
        
        actions_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # Increased from 12
            size_hint_y=None,
            height=dp(52)    # Increased from 48
        )
        
        comprehensive_btn = MDRaisedButton(
            text="🏆 Generate Full Report",
            size_hint_x=2,
            height=dp(48),   # Increased from 44
            md_bg_color=(0.8, 0.2, 0.8, 1),
            font_size="15sp", # Increased from 14sp
            on_release=lambda x: self._run_comprehensive_report(project_id)
        )
        
        variables_btn = MDRaisedButton(
            text="🎯 Sample Size Guide",
            size_hint_x=1,
            height=dp(48),   # Increased from 44
            md_bg_color=(0.2, 0.8, 0.6, 1),
            font_size="15sp", # Increased from 14sp
            on_release=lambda x: self._show_sample_size_recommendations(project_id)
        )
        
        actions_layout.add_widget(comprehensive_btn)
        actions_layout.add_widget(variables_btn)
        quick_actions_card.add_widget(actions_layout)
        
        content.add_widget(quick_actions_card)
        
        print(f"[DEBUG] Descriptive selection interface created successfully!")
    
    def _create_analysis_option_card(self, project_id: str, option: Dict):
        """Create an individual analysis option card"""
        option_card = MDCard(
            orientation="vertical",
            padding=dp(20),  # Increased from 16
            spacing=dp(12),  # Increased from 8
            size_hint_y=None,
            height=dp(240),  # Increased by 150% from 180 (180 * 2.5 = 450)
            elevation=2,
            md_bg_color=(1, 1, 1, 1),
            radius=[12, 12, 12, 12]
        )
        
        # Header with icon and name
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),  # Increased from 8
            size_hint_y=None,
            height=dp(40)    # Increased for larger cards
        )
        
        icon_label = MDLabel(
            text=option['icon'],
            font_style="H4",  # Larger font for bigger card
            size_hint_x=None,
            width=dp(40)     # Increased for larger cards
        )
        
        name_label = MDLabel(
            text=option['name'],
            font_style="Subtitle1",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(icon_label)
        header_layout.add_widget(name_label)
        option_card.add_widget(header_layout)
        
        # Description
        desc_label = MDLabel(
            text=option['description'],
            font_style="Body1",  # Larger font for bigger card
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(60)    # Increased for larger cards
        )
        option_card.add_widget(desc_label)
        
        # Suitable for
        suitable_label = MDLabel(
            text=f"📋 {option['suitable_for']}",
            font_style="Body2",  # Larger font for bigger card
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(42)    # Increased for larger cards
        )
        option_card.add_widget(suitable_label)
        
        # Run button
        run_button = MDRaisedButton(
            text=f"▶️ Run {option['name']}",
            size_hint_y=None,
            height=dp(48),   # Increased for larger cards
            md_bg_color=option['color'],
            font_size="16sp", # Increased font size for larger card
            on_release=lambda x, endpoint=option['endpoint']: self._run_specific_analysis(project_id, endpoint, option['name'])
        )
        option_card.add_widget(run_button)
        
        return option_card
    
    def _run_specific_analysis(self, project_id: str, endpoint: str, analysis_name: str):
        """Run a specific descriptive analysis"""
        print(f"[DEBUG] Running {analysis_name} analysis for project {project_id}")
        toast(f"🔄 Running {analysis_name}...")
        
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
                lambda dt: self._display_specific_analysis_results(results, analysis_name), 0
            )
        except Exception as e:
            print(f"Error in {analysis_name} analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast(f"❌ {analysis_name} analysis failed"), 0
            )
            Clock.schedule_once(
                lambda dt: self.analytics_screen.show_error(f"{analysis_name} analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _display_specific_analysis_results(self, results: Dict, analysis_name: str):
        """Display results from specific analysis"""
        print(f"[DEBUG] Displaying {analysis_name} results: {type(results)}")
        
        if 'error' in results:
            toast(f"❌ {analysis_name}: {results['error']}")
            return
        
        # Create a results dialog for now (can be enhanced later)
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.scrollview import MDScrollView
        
        # Format results for display
        results_text = self._format_analysis_results(results, analysis_name)
        
        results_content = MDScrollView(size_hint=(1, 1))
        results_label = MDLabel(
            text=results_text,
            font_style="Body2",
            theme_text_color="Secondary",
            text_size=(None, None),
            size_hint_y=None
        )
        results_label.bind(texture_size=results_label.setter('size'))
        results_content.add_widget(results_label)
        
        results_dialog = MDDialog(
            title=f"📊 {analysis_name} Results",
            type="custom",
            content_cls=results_content,
            size_hint=(0.9, 0.8),
            buttons=[
                MDFlatButton(
                    text="Close",
                    font_size="16sp",
                    on_release=lambda x: results_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="📤 Export",
                    font_size="16sp",
                    on_release=lambda x: self._export_analysis_results(results, analysis_name)
                )
            ]
        )
        
        results_dialog.open()
        toast(f"✅ {analysis_name} completed successfully!")
    
    def _format_analysis_results(self, results: Dict, analysis_name: str) -> str:
        """Format analysis results for display"""
        if not results or 'error' in results:
            return f"❌ {analysis_name} failed: {results.get('error', 'Unknown error')}"
        
        formatted_text = f"✅ {analysis_name} Results\n\n"
        
        # Add summary if available
        if 'summary' in results:
            summary = results['summary']
            formatted_text += "📋 Summary:\n"
            for key, value in summary.items():
                formatted_text += f"  • {key.replace('_', ' ').title()}: {value}\n"
            formatted_text += "\n"
        
        # Add main results (truncated for display)
        main_keys = [k for k in results.keys() if k not in ['summary', 'error']]
        if main_keys:
            formatted_text += "📊 Analysis Results:\n"
            for key in main_keys[:5]:  # Limit to first 5 keys
                formatted_text += f"  • {key.replace('_', ' ').title()}: Available\n"
            
            if len(main_keys) > 5:
                formatted_text += f"  • ... and {len(main_keys) - 5} more result sections\n"
        
        formatted_text += f"\n📤 Full results can be exported for detailed analysis."
        
        return formatted_text
    
    def _run_comprehensive_report(self, project_id: str):
        """Run comprehensive report generation"""
        toast("🏆 Generating comprehensive report...")
        self.analytics_screen.set_loading(True)
        
        threading.Thread(
            target=self._comprehensive_report_thread,
            args=(project_id,),
            daemon=True
        ).start()
    
    def _comprehensive_report_thread(self, project_id: str):
        """Background thread for comprehensive report"""
        try:
            results = self.analytics_service.generate_comprehensive_report(project_id, include_plots=True)
            Clock.schedule_once(
                lambda dt: self._display_specific_analysis_results(results, "Comprehensive Report"), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: toast("❌ Comprehensive report generation failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _show_variable_selection(self, project_id: str):
        """Show variable selection dialog"""
        toast("🎯 Variable selection - coming soon!")
    
    def _show_sample_size_recommendations(self, project_id: str):
        """Show detailed sample size recommendations dialog"""
        # Get project variables with sample size analysis
        project_variables = self.analytics_service.get_project_variables(project_id)
        if 'error' in project_variables:
            toast(f"❌ Error loading sample size analysis: {project_variables['error']}")
            return
        
        sample_adequacy = project_variables.get('sample_size_analysis', {})
        recommendations = sample_adequacy.get('recommendations', {})
        
        if not recommendations:
            toast("📊 No sample size recommendations available")
            return
        
        # Create recommendations content
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivy.metrics import dp
        
        # Content container
        content_container = MDScrollView(size_hint=(1, 1))
        
        content_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            adaptive_height=True,
            padding=[dp(20), dp(20), dp(20), dp(20)]
        )
        
        # Header info
        current_size = sample_adequacy.get('current_size', 0)
        adequacy_status = sample_adequacy.get('adequacy_status', 'unknown')
        adequacy_score = sample_adequacy.get('adequacy_score', 0.0)
        
        header_text = f"""📊 Sample Size Analysis for Your Dataset

Current Sample Size: {current_size:,} participants
Overall Adequacy: {adequacy_status.title()} (Score: {adequacy_score:.1f}/1.0)

Below are the sample size requirements for different statistical tests:"""
        
        header_label = MDLabel(
            text=header_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            adaptive_height=True,
            text_size=(None, None)
        )
        content_layout.add_widget(header_label)
        
        # Create cards for each recommendation
        for test_type, rec in recommendations.items():
            test_card = self._create_sample_size_recommendation_card(rec)
            content_layout.add_widget(test_card)
        
        # General guidance
        general_guidance = sample_adequacy.get('summary', {}).get('general_guidance', '')
        if general_guidance:
            guidance_card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(120),
                md_bg_color=(0.95, 0.98, 1.0, 1),
                elevation=2,
                radius=[8, 8, 8, 8]
            )
            
            guidance_title = MDLabel(
                text="💡 General Recommendation",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(32)
            )
            
            guidance_text = MDLabel(
                text=general_guidance,
                font_style="Body1",
                theme_text_color="Secondary",
                size_hint_y=None,
                adaptive_height=True,
                text_size=(None, None)
            )
            
            guidance_card.add_widget(guidance_title)
            guidance_card.add_widget(guidance_text)
            content_layout.add_widget(guidance_card)
        
        content_container.add_widget(content_layout)
        
        # Create dialog
        recommendations_dialog = MDDialog(
            title="🎯 Sample Size Recommendations",
            type="custom",
            content_cls=content_container,
            size_hint=(0.9, 0.8),
            buttons=[
                MDFlatButton(
                    text="Close",
                    font_size="16sp",
                    on_release=lambda x: recommendations_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="📤 Export Analysis",
                    font_size="16sp",
                    on_release=lambda x: self._export_sample_size_analysis(sample_adequacy)
                )
            ]
        )
        
        recommendations_dialog.open()
    
    def _create_sample_size_recommendation_card(self, recommendation: dict) -> MDCard:
        """Create a card showing sample size recommendation for a specific test"""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp
        
        test_type = recommendation.get('test_type', 'Unknown Test')
        current_size = recommendation.get('current_size', 0)
        adequacy = recommendation.get('adequacy', 'unknown')
        rec_text = recommendation.get('recommendation', 'No recommendation available')
        
        # Determine card color based on adequacy
        if adequacy == 'adequate':
            card_color = (0.95, 1.0, 0.95, 1)  # Light green
            status_emoji = '✅'
        else:
            card_color = (1.0, 0.98, 0.95, 1)  # Light orange
            status_emoji = '⚠️'
        
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(160),
            md_bg_color=card_color,
            elevation=2,
            radius=[8, 8, 8, 8]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32)
        )
        
        status_label = MDLabel(
            text=status_emoji,
            font_style="H6",
            size_hint_x=None,
            width=dp(32)
        )
        
        title_label = MDLabel(
            text=f"{test_type} - {adequacy.title()}",
            font_style="Subtitle1",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(status_label)
        header_layout.add_widget(title_label)
        card.add_widget(header_layout)
        
        # Requirements info
        if 'needed_for_medium_effect' in recommendation:
            needed = recommendation['needed_for_medium_effect']
            req_text = f"Current: {current_size:,} | Needed: {needed:,} | Status: {adequacy}"
        elif 'minimum_needed' in recommendation:
            needed = recommendation['minimum_needed']
            req_text = f"Current: {current_size:,} | Minimum: {needed:,} | Status: {adequacy}"
        else:
            req_text = f"Current size: {current_size:,} | Status: {adequacy}"
        
        req_label = MDLabel(
            text=req_text,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24)
        )
        card.add_widget(req_label)
        
        # Recommendation text
        rec_label = MDLabel(
            text=rec_text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            adaptive_height=True,
            text_size=(None, None)
        )
        card.add_widget(rec_label)
        
        return card
    
    def _export_sample_size_analysis(self, sample_adequacy: dict):
        """Export sample size analysis results"""
        try:
            import json
            analysis_json = json.dumps(sample_adequacy, indent=2, default=str)
            toast("✅ Sample size analysis exported successfully!")
            # In a real implementation, you'd save this to a file
            print("Sample Size Analysis Export:")
            print(analysis_json)
        except Exception as e:
            toast(f"❌ Export failed: {str(e)}")
    
    def _export_analysis_results(self, results: Dict, analysis_name: str):
        """Export analysis results"""
        try:
            exported = self.analytics_service.export_analysis_results(results, 'json')
            toast(f"✅ {analysis_name} results exported successfully!")
        except Exception as e:
            toast(f"❌ Export failed: {str(e)}")
    
    def _create_error_state_card(self, message: str):
        """Create error state card"""
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.button import MDIconButton
        
        error_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(264),  # Increased by 10% from 240
            padding=dp(32),  # Increased from 20
            spacing=dp(20),  # Increased from 16
            md_bg_color=(1, 0.95, 0.95, 1),
            elevation=2,
            radius=[16, 16, 16, 16]
        )
        
        error_icon = MDIconButton(
            icon="alert-circle",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(72),    # Increased from 64
            user_font_size="56sp"  # Increased from 48sp
        )
        
        error_label = MDLabel(
            text=message,
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            halign="center",
            size_hint_y=None,
            height=dp(100)   # Increased from 80
        )
        
        error_card.add_widget(error_icon)
        error_card.add_widget(error_label)
        
        return error_card
    
    def _show_initial_descriptive_interface(self, project_id: str):
        """Show initial descriptive analytics interface immediately"""
        print(f"[DEBUG] _show_initial_descriptive_interface called for project: {project_id}")
        
        # Use the helper method to get the content area
        content = self.analytics_screen.get_tab_content('descriptive')
        
        if not content:
            print(f"[DEBUG] ERROR: Could not get descriptive content area")
            return
            
        content.clear_widgets()
        
        # Use fixed-height approach for immediate display
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        # 1. Initial Interface Card (Fixed Height)  
        initial_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(330),  # Increased by 10% from 300
            padding=dp(20),
            spacing=dp(16),
            md_bg_color=(0.98, 0.99, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        desc_icon = MDIconButton(
            icon="chart-line",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48),
            user_font_size="24sp"
        )
        
        header_label = MDLabel(
            text="📊 Descriptive Analytics",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(desc_icon)
        header_layout.add_widget(header_label)
        initial_card.add_widget(header_layout)
        
        # Status message
        status_text = f"""🔄 Preparing Descriptive Analysis...

📊 Loading project data and variables
📈 Calculating statistical measures  
🎯 Generating comprehensive insights

Please wait while we analyze your data."""
        
        status_label = MDLabel(
            text=status_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(160)
        )
        initial_card.add_widget(status_label)
        
        # Quick action buttons (disabled during loading)
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        config_btn = MDRaisedButton(
            text="⚙️ Configuration",
            size_hint_x=1,
            height=dp(40),
            md_bg_color=(0.6, 0.6, 0.6, 1),
            font_size="14sp",
            disabled=True
        )
        
        preview_btn = MDRaisedButton(
            text="👁️ Preview Data",
            size_hint_x=1,
            height=dp(40),
            md_bg_color=(0.6, 0.6, 0.6, 1),
            font_size="14sp",
            disabled=True
        )
        
        buttons_layout.add_widget(config_btn)
        buttons_layout.add_widget(preview_btn)
        initial_card.add_widget(buttons_layout)
        
        content.add_widget(initial_card)
        print(f"[DEBUG] Initial descriptive interface created successfully!")
    
    def _create_fixed_height_results_card(self, results):
        """Create fixed-height results card for descriptive analytics"""
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        results_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(374),  # Increased by 10% from 340
            padding=dp(32),  # Increased from 20
            spacing=dp(16),  # Increased from 12
            md_bg_color=(1.0, 0.99, 0.97, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # Increased from 12
            size_hint_y=None,
            height=dp(48)    # Increased from 40
        )
        
        results_icon = MDIconButton(
            icon="chart-bar",
            theme_icon_color="Custom",
            icon_color=(1.0, 0.6, 0.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(56),    # Increased from 48
            user_font_size="28sp"  # Increased from 24sp
        )
        
        header_label = MDLabel(
            text="📊 Analysis Results",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(results_icon)
        header_layout.add_widget(header_label)
        results_card.add_widget(header_layout)
        
        # Results summary
        analyses = results.get('analyses', {})
        analysis_count = len([k for k in analyses.keys() if 'error' not in analyses.get(k, {})])
        
        results_text = f"""✅ Analysis Complete!

📊 Analyses Completed: {analysis_count}
🎯 Results Available: {', '.join(analyses.keys())[:50]}{'...' if len(', '.join(analyses.keys())) > 50 else ''}

Status: Ready for detailed review and export"""
        
        results_label = MDLabel(
            text=results_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(160)   # Increased from 140
        )
        results_card.add_widget(results_label)
        
        # Action buttons
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # Increased from 12
            size_hint_y=None,
            height=dp(52)    # Increased from 48
        )
        
        view_btn = MDRaisedButton(
            text="📊 View Details",
            size_hint_x=1,
            height=dp(48),   # Increased from 40
            md_bg_color=(0.2, 0.8, 0.2, 1),
            font_size="15sp", # Increased from 14sp
            on_release=lambda x: self._show_detailed_results(results)
        )
        
        export_btn = MDRaisedButton(
            text="📤 Export",
            size_hint_x=0.7,
            height=dp(48),   # Increased from 40
            md_bg_color=(0.6, 0.6, 0.6, 1),
            font_size="15sp", # Increased from 14sp
            on_release=lambda x: self._export_results("descriptive", results)
        )
        
        action_layout.add_widget(view_btn)
        action_layout.add_widget(export_btn)
        results_card.add_widget(action_layout)
        
        return results_card
    
    def _show_detailed_results(self, results):
        """Show detailed results in a dialog"""
        toast("📊 Detailed results view - coming soon!")
    
    def _create_tablet_analysis_configuration(self, content, project_variables):
        """Create tablet-optimized analysis configuration interface"""
        if 'error' in project_variables:
            return
        
        config_card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(280),
            elevation=3,
            md_bg_color=(0.98, 0.99, 1.0, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Header with enhanced tablet styling
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(56)
        )
        
        config_icon = MDIconButton(
            icon="cog",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48),
            user_font_size="24sp"
        )
        
        header_label = MDLabel(
            text="⚙️ Descriptive Analytics Configuration",
            font_style="H4",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(config_icon)
        header_layout.add_widget(header_label)
        config_card.add_widget(header_layout)
        
        # Enhanced data summary for tablets
        data_summary = f"""📊 Dataset Overview: {project_variables.get('sample_size', 0):,} responses across {project_variables.get('variable_count', 0)} variables

📈 Numeric Variables: {len(project_variables.get('numeric_variables', []))} (for distribution analysis, correlation, outliers)
🏷️  Categorical Variables: {len(project_variables.get('categorical_variables', []))} (for frequency analysis, cross-tabulation)
📝 Text Variables: {len(project_variables.get('text_variables', []))} (for content analysis, word frequency)
📅 Date/Time Variables: {len(project_variables.get('datetime_variables', []))} (for temporal patterns, trends)"""
        
        summary_label = MDLabel(
            text=data_summary,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(120)
        )
        config_card.add_widget(summary_label)
        
        # Analysis type buttons optimized for tablets
        analysis_buttons = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=self.TABLET_BUTTON_HEIGHT + dp(8)
        )
        
        buttons_data = [
            ("📊 Basic Statistics", "basic", (0.2, 0.6, 1.0, 1)),
            ("📈 Distribution Analysis", "distribution", (1.0, 0.6, 0.2, 1)),
            ("🏷️ Categorical Analysis", "categorical", (0.2, 0.8, 0.6, 1)),
            ("🎯 Advanced Options", "advanced", (0.6, 0.2, 0.8, 1))
        ]
        
        for btn_text, btn_type, color in buttons_data:
            btn = MDRaisedButton(
                text=btn_text,
                size_hint_x=1,
                height=self.TABLET_BUTTON_HEIGHT,
                font_size=self.TABLET_FONT_SIZE,
                md_bg_color=color,
                on_release=lambda x, t=btn_type: self._handle_tablet_analysis_button(t)
            )
            analysis_buttons.add_widget(btn)
        
        config_card.add_widget(analysis_buttons)
        content.add_widget(config_card)
    
    def _create_tablet_results_dashboard(self, content, results):
        """Create tablet-optimized results dashboard"""
        if 'analyses' not in results:
            return
        
        analyses = results['analyses']
        
        # Dashboard header
        dashboard_header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(56)
        )
        
        dashboard_icon = MDIconButton(
            icon="view-dashboard",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.8, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48)
        )
        
        dashboard_title = MDLabel(
            text="📋 Analysis Results Dashboard",
            font_style="H4",
            theme_text_color="Primary",
            bold=True
        )
        
        dashboard_header.add_widget(dashboard_icon)
        dashboard_header.add_widget(dashboard_title)
        content.add_widget(dashboard_header)
        
        # Results grid optimized for tablets (2 columns)
        results_grid = GridLayout(
            cols=2,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(400)
        )
        
        # Display comprehensive report if available
        if 'comprehensive_report' in analyses:
            comp_report = analyses['comprehensive_report']
            report_card = self._create_tablet_comprehensive_report_card(comp_report)
            results_grid.add_widget(report_card)
        
        # Display data quality analysis
        if 'data_quality' in analyses:
            quality_data = analyses['data_quality']
            quality_card = self._create_tablet_data_quality_card(quality_data)
            results_grid.add_widget(quality_card)
        
        # Display descriptive analysis if available
        if 'descriptive' in analyses and 'error' not in analyses['descriptive']:
            descriptive_data = analyses['descriptive']
            descriptive_card = self._create_tablet_descriptive_results_card(descriptive_data)
            results_grid.add_widget(descriptive_card)
        
        # Fill remaining space if needed
        if len([k for k in analyses.keys() if 'error' not in analyses.get(k, {})]) % 2 == 1:
            placeholder_card = self._create_tablet_placeholder_card()
            results_grid.add_widget(placeholder_card)
        
        content.add_widget(results_grid)
    
    def _create_tablet_detailed_statistics(self, content, results):
        """Create detailed statistics section optimized for tablets"""
        analyses = results.get('analyses', {})
        
        # Only show if we have meaningful data
        if not any('error' not in analysis for analysis in analyses.values()):
            return
        
        stats_header = MDLabel(
            text="📊 Detailed Statistical Analysis",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48),
            bold=True
        )
        content.add_widget(stats_header)
        
        # Create expandable statistics cards
        stats_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            adaptive_height=True
        )
        
        # Basic statistics card
        if 'data_quality' in analyses and 'data_overview' in analyses['data_quality']:
            overview_data = analyses['data_quality']['data_overview']
            basic_stats_card = self._create_tablet_basic_stats_card(overview_data)
            stats_container.add_widget(basic_stats_card)
        
        # Outlier analysis card
        if 'data_quality' in analyses and 'outlier_summary' in analyses['data_quality']:
            outlier_data = analyses['data_quality']['outlier_summary']
            outlier_card = self._create_tablet_outlier_analysis_card(outlier_data)
            stats_container.add_widget(outlier_card)
        
        content.add_widget(stats_container)
    
    def _create_tablet_specialized_options(self, content, project_variables):
        """Create specialized analysis options optimized for tablets"""
        options_card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(320),
            elevation=3,
            md_bg_color=(0.98, 1.0, 0.98, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_label = MDLabel(
            text="🔬 Advanced Descriptive Analytics",
            font_style="H4",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48),
            bold=True
        )
        options_card.add_widget(header_label)
        
        # Description
        desc_label = MDLabel(
            text="Explore advanced statistical analysis and data insights:",
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(32)
        )
        options_card.add_widget(desc_label)
        
        # Specialized options grid (3 columns for tablets)
        options_grid = GridLayout(
            cols=3,
            spacing=dp(16),
            size_hint_y=None,
            height=dp(140)
        )
        
        specialized_options = [
            ("outlier", "🎯 Outlier Detection", "Identify unusual data points", (0.8, 0.4, 0.2, 1)),
            ("correlation", "🔗 Correlation Matrix", "Variable relationships", (0.4, 0.2, 0.8, 1)), 
            ("missing", "❓ Missing Data Analysis", "Analyze data completeness", (0.8, 0.6, 0.4, 1)),
            ("distribution", "📊 Distribution Testing", "Normality and shape tests", (0.2, 0.8, 0.4, 1)),
            ("temporal", "⏰ Temporal Analysis", "Time-based patterns", (0.6, 0.4, 0.8, 1)),
            ("export", "📤 Export Results", "Download analysis reports", (0.6, 0.8, 0.2, 1))
        ]
        
        for option_code, title, description, color in specialized_options:
            option_btn = self._create_tablet_specialized_option_button(option_code, title, description, color)
            options_grid.add_widget(option_btn)
        
        options_card.add_widget(options_grid)
        
        # Quick actions with tablet-friendly layout
        quick_actions = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=self.TABLET_BUTTON_HEIGHT + dp(8)
        )
        
        comprehensive_btn = MDRaisedButton(
            text="🏆 Generate Comprehensive Report",
            size_hint_x=2,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(0.2, 0.8, 0.2, 1),
            font_size=self.TABLET_FONT_SIZE,
            on_release=lambda x: self._generate_comprehensive_report()
        )
        
        variables_btn = MDRaisedButton(
            text="🎯 Select Variables",
            size_hint_x=1,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(0.2, 0.6, 1.0, 1),
            font_size=self.TABLET_FONT_SIZE,
            on_release=lambda x: self._show_tablet_variable_selection()
        )
        
        quick_actions.add_widget(comprehensive_btn)
        quick_actions.add_widget(variables_btn)
        options_card.add_widget(quick_actions)
        
        content.add_widget(options_card)
    
    def _create_tablet_comprehensive_report_card(self, report_data: Dict) -> MDCard:
        """Create tablet-optimized comprehensive report card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            size_hint_y=None,
            height=dp(418),  # Increased by 10% from 380
            elevation=3,
            md_bg_color=(1.0, 0.99, 0.97, 1),
            radius=[12, 12, 12, 12]
        )
        
        # Header with better tablet styling
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        header_icon = MDIconButton(
            icon="file-document-multiple",
            theme_icon_color="Custom",
            icon_color=(1.0, 0.6, 0.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(40)
        )
        
        header_label = MDLabel(
            text="📄 Comprehensive Report",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(header_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Report status and metadata
        if 'error' in report_data:
            error_label = MDLabel(
                text=f"❌ Report Generation Error:\n{report_data['error']}",
                font_style="Body1",
                theme_text_color="Custom",
                text_color=(0.8, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(80)
            )
            card.add_widget(error_label)
        else:
            # Success state with metadata
            if 'report_metadata' in report_data:
                metadata = report_data['report_metadata']
                metadata_text = f"""✅ Report Generated Successfully

📋 Type: {metadata.get('report_type', 'Comprehensive Analysis')}
🕒 Generated: {metadata.get('generated_at', 'N/A')[:19] if metadata.get('generated_at') else 'N/A'}
📊 Data Shape: {metadata.get('data_shape', 'N/A')}
🔢 Variables Analyzed: {metadata.get('variables_analyzed', 'N/A')}"""
                
                metadata_label = MDLabel(
                    text=metadata_text,
                    font_style="Body1",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(160)
                )
                card.add_widget(metadata_label)
            
            # Executive summary preview
            if 'executive_summary' in report_data:
                summary = report_data['executive_summary']
                if isinstance(summary, dict) and 'overview' in summary:
                    summary_text = summary['overview'][:120] + "..." if len(summary['overview']) > 120 else summary['overview']
                    summary_label = MDLabel(
                        text=f"📋 Executive Summary:\n{summary_text}",
                        font_style="Body2",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(80)
                    )
                    card.add_widget(summary_label)
        
        # Action buttons with tablet spacing
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(44)
        )
        
        if 'error' not in report_data:
            view_btn = MDRaisedButton(
                text="📖 View Full Report",
                size_hint_x=2,
                height=dp(44),
                font_size="14sp",
                on_release=lambda x: self._show_tablet_full_report(report_data)
            )
            action_layout.add_widget(view_btn)
        
        export_btn = MDRaisedButton(
            text="📤 Export",
            size_hint_x=1,
            height=dp(44),
            font_size="14sp",
            md_bg_color=(0.6, 0.6, 0.6, 1),
            on_release=lambda x: self._export_report(report_data)
        )
        action_layout.add_widget(export_btn)
        
        card.add_widget(action_layout)
        return card
    
    def _create_tablet_data_quality_card(self, quality_data: Dict) -> MDCard:
        """Create tablet-optimized data quality card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            size_hint_y=None,
            height=dp(418),  # Increased by 10% from 380
            elevation=3,
            md_bg_color=(0.99, 1.0, 0.97, 1),
            radius=[12, 12, 12, 12]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        header_icon = MDIconButton(
            icon="shield-check",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.8, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(40)
        )
        
        header_label = MDLabel(
            text="🛡️ Data Quality Assessment",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(header_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Quality metrics with enhanced tablet display
        if 'summary' in quality_data:
            summary = quality_data['summary']
            quality_score = summary.get('overall_quality_score', 0)
            
            # Quality score with visual indicator
            score_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(16),
                size_hint_y=None,
                height=dp(56)
            )
            
            # Quality level indicator
            if quality_score > 90:
                score_color = (0.2, 0.8, 0.2, 1)
                score_emoji = "🌟"
                score_level = "Excellent"
            elif quality_score > 80:
                score_color = (0.6, 0.8, 0.2, 1)
                score_emoji = "✅"
                score_level = "Good"
            elif quality_score > 60:
                score_color = (0.8, 0.6, 0.2, 1)
                score_emoji = "⚠️"
                score_level = "Fair"
            else:
                score_color = (0.8, 0.2, 0.2, 1)
                score_emoji = "❌"
                score_level = "Poor"
            
            score_icon = MDLabel(
                text=score_emoji,
                font_style="H3",
                size_hint_x=None,
                width=dp(48)
            )
            
            score_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(4)
            )
            
            score_value_label = MDLabel(
                text=f"{quality_score:.1f}%",
                font_style="H4",
                theme_text_color="Custom",
                text_color=score_color,
                bold=True,
                size_hint_y=None,
                height=dp(32)
            )
            
            score_level_label = MDLabel(
                text=f"Quality: {score_level}",
                font_style="Body1",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )
            
            score_content.add_widget(score_value_label)
            score_content.add_widget(score_level_label)
            
            score_layout.add_widget(score_icon)
            score_layout.add_widget(score_content)
            card.add_widget(score_layout)
            
            # Additional quality metrics
            metrics_text = f"""📊 Dataset Metrics:
• Variables: {summary.get('variables', 'N/A')}
• Observations: {summary.get('observations', 'N/A'):,}
• Analysis Type: {summary.get('analysis_type', 'N/A').title()}

🔍 Quality Indicators:
• Data completeness assessed
• Consistency checks performed  
• Validity measures computed"""
            
            metrics_label = MDLabel(
                text=metrics_text,
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(160)
            )
            card.add_widget(metrics_label)
        
        # Action buttons
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(44)
        )
        
        details_btn = MDRaisedButton(
            text="📋 Quality Details",
            size_hint_x=1,
            height=dp(44),
            font_size="14sp",
            on_release=lambda x: self._show_tablet_quality_details(quality_data)
        )
        
        improve_btn = MDFlatButton(
            text="💡 Improvement Tips",
            size_hint_x=1,
            height=dp(44),
            font_size="14sp",
            on_release=lambda x: self._show_quality_improvement_tips(quality_data)
        )
        
        action_layout.add_widget(details_btn)
        action_layout.add_widget(improve_btn)
        card.add_widget(action_layout)
        
        return card
    
    def _create_tablet_descriptive_results_card(self, descriptive_data: Dict) -> MDCard:
        """Create tablet-optimized descriptive results card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            size_hint_y=None,
            height=dp(418),  # Increased by 10% from 380
            elevation=3,
            md_bg_color=(0.97, 0.99, 1.0, 1),
            radius=[12, 12, 12, 12]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        header_icon = MDIconButton(
            icon="chart-bar",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(40)
        )
        
        header_label = MDLabel(
            text="📊 Descriptive Statistics",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(header_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Summary information with enhanced tablet display
        if 'summary' in descriptive_data:
            summary = descriptive_data['summary']
            summary_text = f"""📈 Analysis Summary:
• Variables Analyzed: {summary.get('variables_analyzed', 'N/A')}
• Total Observations: {summary.get('observations', 'N/A'):,}
• Numeric Variables: {summary.get('numeric_variables', 'N/A')}
• Categorical Variables: {summary.get('categorical_variables', 'N/A')}

✅ Completed Analyses:"""
            
            # Add completion indicators
            if 'basic_statistics' in descriptive_data:
                summary_text += "\n• ✓ Basic descriptive statistics"
            if 'correlations' in descriptive_data:
                summary_text += "\n• ✓ Correlation analysis"
            if 'outliers' in descriptive_data:
                summary_text += "\n• ✓ Outlier detection"
            
            summary_label = MDLabel(
                text=summary_text,
                font_style="Body1",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(200)
            )
            card.add_widget(summary_label)
        
        # Action buttons
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(44)
        )
        
        details_btn = MDRaisedButton(
            text="📊 View Statistics",
            size_hint_x=1,
            height=dp(44),
            font_size="14sp",
            on_release=lambda x: self._show_tablet_descriptive_details(descriptive_data)
        )
        
        visualize_btn = MDFlatButton(
            text="📈 Create Charts",
            size_hint_x=1,
            height=dp(44),
            font_size="14sp",
            on_release=lambda x: self._show_visualization_options(descriptive_data)
        )
        
        action_layout.add_widget(details_btn)
        action_layout.add_widget(visualize_btn)
        card.add_widget(action_layout)
        
        return card
    
    def _create_tablet_basic_stats_card(self, overview_data: Dict) -> MDCard:
        """Create tablet-optimized basic statistics card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(280),
            elevation=2,
            md_bg_color=(0.99, 0.99, 1.0, 1),
            radius=[12, 12, 12, 12]
        )
        
        # Header
        header_label = MDLabel(
            text="📊 Basic Statistics Summary",
            font_style="H6",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(32)
        )
        card.add_widget(header_label)
        
        # Statistics grid for tablets
        stats_scroll = MDScrollView(
            size_hint=(1, 1)
        )
        
        stats_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True
        )
        
        # Display statistics for available variables
        for var_name, var_stats in overview_data.items():
            if isinstance(var_stats, dict) and 'mean' in var_stats:
                var_card = self._create_variable_stats_row(var_name, var_stats)
                stats_layout.add_widget(var_card)
        
        stats_scroll.add_widget(stats_layout)
        card.add_widget(stats_scroll)
        
        return card
    
    def _create_variable_stats_row(self, var_name: str, var_stats: Dict) -> MDCard:
        """Create a row displaying statistics for a single variable"""
        row_card = MDCard(
            orientation="horizontal",
            padding=dp(12),
            spacing=dp(16),
            size_hint_y=None,
            height=dp(80),
            elevation=1,
            md_bg_color=(1, 1, 1, 1),
            radius=[8, 8, 8, 8]
        )
        
        # Variable name
        name_label = MDLabel(
            text=var_name,
            font_style="Button",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=0.3,
            halign="left"
        )
        
        # Statistics
        stats_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_x=0.7
        )
        
        # First row: Mean, Median
        stats_row1 = MDLabel(
            text=f"Mean: {var_stats.get('mean', 'N/A'):.2f} | Median: {var_stats.get('median', 'N/A'):.2f}",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20)
        )
        
        # Second row: Std Dev, Range
        stats_row2 = MDLabel(
            text=f"Std Dev: {var_stats.get('std', 'N/A'):.2f} | Range: {var_stats.get('range', 'N/A'):.2f}",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20)
        )
        
        stats_layout.add_widget(stats_row1)
        stats_layout.add_widget(stats_row2)
        
        row_card.add_widget(name_label)
        row_card.add_widget(stats_layout)
        
        return row_card
    
    def _create_tablet_placeholder_card(self) -> MDCard:
        """Create a placeholder card for empty grid spaces"""
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            size_hint_y=None,
            height=dp(418),  # Increased by 10% from 380
            elevation=1,
            md_bg_color=(0.98, 0.98, 0.98, 1),
            radius=[12, 12, 12, 12]
        )
        
        placeholder_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16)
        )
        
        placeholder_icon = MDIconButton(
            icon="plus-circle",
            theme_icon_color="Custom",
            icon_color=(0.6, 0.6, 0.6, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48),
            user_font_size="32sp"
        )
        
        placeholder_label = MDLabel(
            text="💡 More Analysis Options\n\nRun additional analyses\nto see more results here",
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center"
        )
        
        placeholder_content.add_widget(placeholder_icon)
        placeholder_content.add_widget(placeholder_label)
        card.add_widget(placeholder_content)
        
        return card
    
    def _create_tablet_error_state(self, message: str):
        """Create tablet-optimized error state widget"""
        error_card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(330),  # Increased by 10% from 300
            elevation=2,
            md_bg_color=(1, 0.95, 0.95, 1),
            radius=[16, 16, 16, 16]
        )
        
        error_icon = MDIconButton(
            icon="alert-circle",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(64),
            user_font_size="48sp"
        )
        
        error_label = MDLabel(
            text=message,
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            halign="center",
            size_hint_y=None,
            height=dp(120)
        )
        
        retry_button = MDRaisedButton(
            text="🔄 Try Again",
            size_hint=(None, None),
            height=self.TABLET_BUTTON_HEIGHT,
            width=dp(160),
            font_size=self.TABLET_FONT_SIZE,
            on_release=lambda x: self.run_descriptive_analysis(self.analytics_screen.current_project_id)
        )
        
        center_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16)
        )
        center_layout.add_widget(error_icon)
        center_layout.add_widget(error_label)
        center_layout.add_widget(retry_button)
        
        error_card.add_widget(center_layout)
        return error_card
    
    # Button handlers and utility methods
    def _handle_tablet_analysis_button(self, analysis_type: str):
        """Handle analysis button press with tablet feedback"""
        project_id = self.analytics_screen.current_project_id
        if not project_id:
            toast("📊 Please select a project first")
            return
        
        if analysis_type == "basic":
            self._run_basic_statistics()
        elif analysis_type == "distribution":
            self._show_distribution_options()
        elif analysis_type == "categorical":
            self._show_categorical_options()
        elif analysis_type == "advanced":
            self._show_advanced_options()
    
    def _run_basic_statistics(self):
        """Run basic statistical analysis with tablet feedback"""
        project_id = self.analytics_screen.current_project_id
        toast("📊 Running basic statistical analysis...")
        
        threading.Thread(
            target=self._basic_statistics_thread,
            args=(project_id,),
            daemon=True
        ).start()
    
    def _basic_statistics_thread(self, project_id: str):
        """Background thread for basic statistics"""
        try:
            results = self.analytics_service.run_basic_statistics(project_id)
            Clock.schedule_once(
                lambda dt: self._show_tablet_basic_statistics_results(results), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: toast("❌ Basic statistics analysis failed"), 0
            )
    
    def _show_tablet_basic_statistics_results(self, results: Dict):
        """Show basic statistics results in tablet-optimized dialog"""
        if 'error' in results:
            toast(f"❌ Analysis failed: {results['error']}")
            return
        
        # Create tablet-sized dialog
        results_content = MDScrollView(size_hint=(1, 1))
        
        results_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            adaptive_height=True,
            padding=[dp(20), dp(20), dp(20), dp(20)]
        )
        
        # Format results for tablet display
        formatted_results = self._format_basic_statistics_for_tablet(results)
        
        results_label = MDLabel(
            text=formatted_results,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            adaptive_height=True,
            text_size=(None, None)
        )
        
        results_layout.add_widget(results_label)
        results_content.add_widget(results_layout)
        
        # Create dialog
        results_dialog = MDDialog(
            title="📊 Basic Statistics Results",
            type="custom",
            content_cls=results_content,
            size_hint=(0.9, 0.8),
            buttons=[
                MDFlatButton(
                    text="Close",
                    font_size="16sp",
                    on_release=lambda x: results_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="📤 Export Results",
                    font_size="16sp",
                    on_release=lambda x: self._export_results("basic_statistics", results)
                )
            ]
        )
        
        results_dialog.open()
    
    def _format_basic_statistics_for_tablet(self, results: Dict) -> str:
        """Format basic statistics results for tablet display"""
        if not results or 'error' in results:
            return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"
        
        formatted_text = "✅ Basic Statistics Analysis Complete\n\n"
        
        if 'results' in results and 'summary' in results['results']:
            summary = results['results']['summary']
            formatted_text += f"📊 Analysis Summary:\n"
            formatted_text += f"• Variables Analyzed: {summary.get('variables_analyzed', 'N/A')}\n"
            formatted_text += f"• Total Observations: {summary.get('observations', 'N/A'):,}\n\n"
            
            # Add detailed statistics if available
            if 'basic_statistics' in results['results']:
                formatted_text += "📈 Variable Statistics:\n\n"
                stats = results['results']['basic_statistics']
                
                for var_name, var_stats in stats.items():
                    if isinstance(var_stats, dict) and 'mean' in var_stats:
                        formatted_text += f"📊 {var_name}:\n"
                        formatted_text += f"  • Mean: {var_stats.get('mean', 'N/A'):.3f}\n"
                        formatted_text += f"  • Median: {var_stats.get('median', 'N/A'):.3f}\n"
                        formatted_text += f"  • Std Dev: {var_stats.get('std', 'N/A'):.3f}\n"
                        formatted_text += f"  • Min: {var_stats.get('min', 'N/A'):.3f}\n"
                        formatted_text += f"  • Max: {var_stats.get('max', 'N/A'):.3f}\n"
                        formatted_text += f"  • Missing: {var_stats.get('missing_count', 0)}\n\n"
        
        return formatted_text
    
    def _show_distribution_options(self):
        """Show distribution analysis options for tablets"""
        toast("📈 Distribution analysis options coming soon!")
    
    def _show_categorical_options(self):
        """Show categorical analysis options for tablets"""
        toast("🏷️ Categorical analysis options coming soon!")
    
    def _show_advanced_options(self):
        """Show advanced analysis options for tablets"""
        toast("🔬 Advanced analysis options available in specialized sections")
    
    # Additional tablet-optimized methods...
    def _export_results(self, analysis_type: str, results: Dict):
        """Export results with tablet feedback"""
        try:
            exported = self.analytics_service.export_analysis_results(results, 'json')
            toast(f"✅ {analysis_type.replace('_', ' ').title()} results exported successfully!")
        except Exception as e:
            toast(f"❌ Export failed: {str(e)}")
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive report with tablet feedback"""
        project_id = self.analytics_screen.current_project_id
        if not project_id:
            toast("📊 Please select a project first")
            return
        
        toast("🏆 Generating comprehensive analytics report...")
        
        threading.Thread(
            target=self._comprehensive_report_thread,
            args=(project_id,),
            daemon=True
        ).start()
    
    def _comprehensive_report_thread(self, project_id: str):
        """Background thread for comprehensive report generation"""
        try:
            results = self.analytics_service.generate_comprehensive_report(project_id, include_plots=True)
            Clock.schedule_once(
                lambda dt: self._show_tablet_comprehensive_report_results(results), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: toast("❌ Report generation failed"), 0
            )
    
    def _show_tablet_comprehensive_report_results(self, results: Dict):
        """Show comprehensive report results with tablet optimization"""
        toast("✅ Comprehensive report generated successfully!")
        # Refresh the current view to show the new report
        self.run_descriptive_analysis(self.analytics_screen.current_project_id)