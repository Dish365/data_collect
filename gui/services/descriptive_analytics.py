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
        """Run comprehensive descriptive analysis optimized for tablets"""
        if not project_id:
            return
            
        self.analytics_screen.set_loading(True)
        toast("📊 Loading comprehensive descriptive analytics...")
        
        threading.Thread(
            target=self._run_descriptive_thread,
            args=(project_id, analysis_config),
            daemon=True
        ).start()
    
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
        if not hasattr(self.analytics_screen.ids, 'descriptive_content'):
            return
            
        content = self.analytics_screen.ids.descriptive_content
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
        
        # Create main scroll container
        main_scroll = MDScrollView()
        main_content = MDBoxLayout(
            orientation="vertical",
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            adaptive_height=True,
            padding=[self.TABLET_PADDING, self.TABLET_PADDING, self.TABLET_PADDING, self.TABLET_PADDING]
        )
        
        # Create tablet-optimized sections
        self._create_tablet_analysis_configuration(main_content, project_variables)
        self._create_tablet_results_dashboard(main_content, results)
        self._create_tablet_detailed_statistics(main_content, results)
        self._create_tablet_specialized_options(main_content, project_variables)
        
        main_scroll.add_widget(main_content)
        content.add_widget(main_scroll)
    
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
            height=dp(380),
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
            height=dp(380),
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
            height=dp(380),
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
            height=dp(380),
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
            height=dp(300),
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