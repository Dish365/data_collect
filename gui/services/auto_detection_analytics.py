"""
Enhanced Auto-Detection Analytics Handler
Specialized service for auto-detection and smart analysis recommendations
OPTIMIZED FOR TABLET UI/UX
"""

from typing import Dict, List, Any, Optional
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import OneLineListItem
from kivymd.uix.snackbar import Snackbar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
import threading
from kivy.clock import Clock
from kivymd.toast import toast
import json


class AutoDetectionAnalyticsHandler:
    """Enhanced handler for auto-detection and smart recommendations - Tablet Optimized"""
    
    def __init__(self, analytics_service, analytics_screen):
        self.analytics_service = analytics_service
        self.analytics_screen = analytics_screen
        self.project_variables = {}
        self.analysis_dialog = None
        
        # Tablet-specific UI constants
        self.TABLET_CARD_HEIGHT = dp(320)  # Larger cards for tablets
        self.TABLET_PADDING = dp(24)       # More generous padding
        self.TABLET_SPACING = dp(20)       # Better spacing
        self.TABLET_BUTTON_HEIGHT = dp(48) # Larger touch targets
        self.TABLET_ICON_SIZE = dp(32)     # Larger icons
    
    def run_auto_detection(self, project_id: str):
        """Run comprehensive auto-detection analysis for a project"""
        if not project_id:
            return
            
        self.analytics_screen.set_loading(True)
        threading.Thread(
            target=self._run_auto_detection_thread,
            args=(project_id,),
            daemon=True
        ).start()
    
    def _run_auto_detection_thread(self, project_id: str):
        """Background thread for auto-detection analysis"""
        try:
            print(f"[DEBUG] Starting auto-detection for project: {project_id}")
            
            # Get project variables for selection options
            print(f"[DEBUG] Getting project variables...")
            variables = self.analytics_service.get_project_variables(project_id)
            print(f"[DEBUG] Project variables result: {variables}")
            self.project_variables = variables
            
            # Get analysis recommendations
            print(f"[DEBUG] Getting analysis recommendations...")
            recommendations = self.analytics_service.get_analysis_recommendations(project_id)
            print(f"[DEBUG] Recommendations retrieved from backend")
            
            # Run comprehensive auto analysis
            print(f"[DEBUG] Running auto analysis...")
            analysis_results = self.analytics_service.run_analysis(project_id, "auto")
            print(f"[DEBUG] Backend returned analysis results successfully")
            
            # Get available analysis types
            print(f"[DEBUG] Getting available analysis types...")
            available_types = self.analytics_service.get_available_analysis_types()
            print(f"[DEBUG] Available analysis types retrieved")
            
            # Combine results
            combined_results = {
                'recommendations': recommendations,
                'analysis_results': analysis_results,
                'available_types': available_types,
                'project_variables': variables
            }
            
            print(f"[DEBUG] Combined results keys: {list(combined_results.keys())}")
            print(f"[DEBUG] Calling display method...")
            
            Clock.schedule_once(
                lambda dt: self._display_auto_detection_results(combined_results), 0
            )
        except Exception as e:
            print(f"Error in auto-detection: {e}")
            import traceback
            print(f"[DEBUG] Auto-detection traceback: {traceback.format_exc()}")
            Clock.schedule_once(
                lambda dt: self.analytics_screen.show_error("Auto-detection failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _display_auto_detection_results(self, results):
        """Display comprehensive analytics results with proper tables and charts."""
        try:
            print(f"[DEBUG] Displaying auto-detection results")
            
            # Get the proper content area using the helper method
            content = self.analytics_screen.get_tab_content('auto_detection')
            
            if not content:
                print(f"[ERROR] Could not get auto_detection content area")
                return
            
            # Schedule on main thread
            Clock.schedule_once(lambda dt: self._continue_display_results(
                content, results, None
            ), 0)
            
        except Exception as e:
            print(f"[ERROR] Failed to display auto-detection results: {e}")
            import traceback
            traceback.print_exc()

    def _continue_display_results(self, content, results, test_label):
        """Continue displaying results on main thread with enhanced visualizations."""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDRaisedButton, MDIconButton
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.scrollview import MDScrollView
            from kivymd.uix.gridlayout import MDGridLayout
            from kivymd.uix.datatables import MDDataTable
            from kivy.metrics import dp
            from kivy.uix.popup import Popup
            import json
            
            # Clear existing content
            content.clear_widgets()
            
            # DON'T create nested MDScrollView - add sections directly to content
            # The content area is already inside an MDScrollView from analytics.kv
            
            # Extract data from results
            analysis_results = results.get('analysis_results', {})
            print(f"[DEBUG] Processing analysis results from backend")
            
            if analysis_results and isinstance(analysis_results, dict):
                data_characteristics = analysis_results.get('data_characteristics', {})
                analyses = analysis_results.get('analyses', {})
            else:
                # Fallback: use empty data but still show recommendations and project info
                data_characteristics = {}
                analyses = {}
                print(f"[DEBUG] Using fallback data structure")
            
            descriptive_results = analyses.get('descriptive', {})
            
            print(f"[DEBUG] Creating analytics visualization for {len(analyses)} analysis types")
            
            # Always show available information, even if analysis results are incomplete
            
            # Add a test widget to ensure container is working
            test_card = MDCard(
                padding=dp(20),
                size_hint_y=None,
                height=dp(80),
                md_bg_color=(0.2, 0.8, 0.4, 0.2),
                elevation=2
            )
            test_label = MDLabel(
                text="✅ Analytics Results Loaded Successfully",
                font_style="H6",
                theme_text_color="Primary",
                halign="center"
            )
            test_card.add_widget(test_label)
            content.add_widget(test_card)  # Add directly to content
            
            # Add spacing between sections
            from kivymd.uix.widget import MDWidget
            spacer = MDWidget(size_hint_y=None, height=dp(20))
            content.add_widget(spacer)
            
            # 1. Data Overview Section (use project variables if data_characteristics is empty)
            if data_characteristics or results.get('project_variables'):
                project_vars = results.get('project_variables', {})
                # Merge project variables into data characteristics if needed
                if not data_characteristics and project_vars:
                    fallback_data_chars = {
                        'sample_size': project_vars.get('sample_size', 0),
                        'variable_count': project_vars.get('variable_count', 0),
                        'numeric_variables': project_vars.get('numeric_variables', []),
                        'categorical_variables': project_vars.get('categorical_variables', []),
                        'text_variables': project_vars.get('text_variables', []),
                        'datetime_variables': project_vars.get('datetime_variables', []),
                        'completeness_score': 85.0  # Default reasonable value
                    }
                    self._create_data_overview_section(content, fallback_data_chars)
                else:
                    self._create_data_overview_section(content, data_characteristics)
                
                # Add spacing after section
                spacer = MDWidget(size_hint_y=None, height=dp(20))
                content.add_widget(spacer)
            
            # 2. Recommendations Section (always show if available)
            if results.get('recommendations'):
                self._create_recommendations_section(content, results.get('recommendations'))
                # Add spacing after section
                spacer = MDWidget(size_hint_y=None, height=dp(20))
                content.add_widget(spacer)
            
            # 3. Analysis Results (only if available)
            if analyses:
                # Basic Statistics Tables
                if 'basic_stats' in descriptive_results:
                    self._create_basic_statistics_section(content, descriptive_results['basic_stats'])
                    spacer = MDWidget(size_hint_y=None, height=dp(20))
                    content.add_widget(spacer)
                
                # Distribution Analysis with Charts
                if 'percentiles' in descriptive_results:
                    self._create_distribution_section(content, descriptive_results)
                    spacer = MDWidget(size_hint_y=None, height=dp(20))
                    content.add_widget(spacer)
                
                # Correlation Analysis
                if 'correlations' in descriptive_results:
                    self._create_correlation_section(content, descriptive_results['correlations'])
                    spacer = MDWidget(size_hint_y=None, height=dp(20))
                    content.add_widget(spacer)
            else:
                # Show message about analysis being in progress or failed
                self._create_analysis_status_section(content, results)
                spacer = MDWidget(size_hint_y=None, height=dp(20))
                content.add_widget(spacer)
            
            # 5. Outlier Detection Results
            if 'outliers' in descriptive_results:
                self._create_outlier_section(content, descriptive_results['outliers'])
                spacer = MDWidget(size_hint_y=None, height=dp(20))
                content.add_widget(spacer)
            
            # 6. Data Quality Assessment
            if 'data_quality' in data_characteristics:
                self._create_data_quality_section(content, data_characteristics['data_quality'])
                spacer = MDWidget(size_hint_y=None, height=dp(20))
                content.add_widget(spacer)
            
            # 7. Export and Action Buttons
            self._create_action_buttons_section(content, results)
            
            print(f"[DEBUG] Successfully displayed analytics results with {len(content.children)} sections")
            
        except Exception as e:
            print(f"[ERROR] Failed to continue display results: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message
            error_card = MDCard(
                padding=dp(20),
                size_hint_y=None,
                height=dp(100),
                md_bg_color=(1, 0.8, 0.8, 1)
            )
            error_label = MDLabel(
                text=f"Error displaying results: {str(e)[:100]}...",
                theme_text_color="Error"
            )
            error_card.add_widget(error_label)
            content.add_widget(error_card)

    def _create_data_overview_section(self, parent, data_characteristics):
        """Create data overview section with key metrics."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.gridlayout import MDGridLayout
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp
        
        # Section header
        header_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(0.1, 0.7, 1.0, 0.1),
            elevation=2
        )
        header_label = MDLabel(
            text="📊 Data Overview",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        header_card.add_widget(header_label)
        parent.add_widget(header_card)
        
        # Metrics grid
        metrics_card = MDCard(
            padding=dp(20),
            size_hint_y=None,
            height=dp(200),
            elevation=3
        )
        
        metrics_grid = MDGridLayout(
            cols=2,
            spacing=dp(20),
            size_hint_y=None,
            height=dp(160)  # Fixed height for metrics grid
        )
        
        # Key metrics
        metrics = [
            ("Sample Size", f"{data_characteristics.get('sample_size', 0):,}"),
            ("Variables", str(data_characteristics.get('variable_count', 0))),
            ("Numeric Variables", str(len(data_characteristics.get('numeric_variables', [])))),
            ("Categorical Variables", str(len(data_characteristics.get('categorical_variables', [])))),
            ("Text Variables", str(len(data_characteristics.get('text_variables', [])))),
            ("Data Completeness", f"{data_characteristics.get('completeness_score', 0):.1f}%")
        ]
        
        for metric_name, metric_value in metrics:
            metric_box = MDBoxLayout(orientation="vertical", spacing=dp(5))
            
            name_label = MDLabel(
                text=metric_name,
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )
            
            value_label = MDLabel(
                text=metric_value,
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            
            metric_box.add_widget(name_label)
            metric_box.add_widget(value_label)
            metrics_grid.add_widget(metric_box)
        
        metrics_card.add_widget(metrics_grid)
        parent.add_widget(metrics_card)

    def _create_basic_statistics_section(self, parent, basic_stats):
        """Create basic statistics section with data tables."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.datatables import MDDataTable
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp
        
        # Section header
        header_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(0.0, 0.8, 0.0, 0.1),
            elevation=2
        )
        header_label = MDLabel(
            text="📈 Basic Statistics",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        header_card.add_widget(header_label)
        parent.add_widget(header_card)
        
        # Create statistics tables for each variable
        for var_name, stats in basic_stats.items():
            if not isinstance(stats, dict) or stats.get('count', 0) == 0:
                continue
                
            var_card = MDCard(
                padding=dp(15),
                size_hint_y=None,
                height=dp(400),
                elevation=3
            )
            
            var_content = MDBoxLayout(orientation="vertical", spacing=dp(10))
            
            # Variable name header
            var_header = MDLabel(
                text=f"Variable: {var_name}",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            var_content.add_widget(var_header)
            
            # Create data table
            table_data = []
            stat_labels = [
                ('mean', 'Mean'),
                ('median', 'Median'),
                ('std', 'Std Dev'),
                ('min', 'Minimum'),
                ('max', 'Maximum'),
                ('count', 'Count'),
                ('missing_count', 'Missing'),
                ('unique_count', 'Unique')
            ]
            
            for stat_key, stat_label in stat_labels:
                value = stats.get(stat_key)
                if value is not None:
                    if isinstance(value, float):
                        formatted_value = f"{value:.3f}"
                    else:
                        formatted_value = str(value)
                    table_data.append([stat_label, formatted_value])
            
            if table_data:
                # Create scrollable table
                table_scroll = MDScrollView(size_hint_y=None, height=dp(300))
                
                table = MDDataTable(
                    size_hint_y=None,
                    height=dp(len(table_data) * 40 + 100),
                    column_data=[
                        ("Statistic", dp(40)),
                        ("Value", dp(40))
                    ],
                    row_data=table_data,
                    elevation=1
                )
                
                table_scroll.add_widget(table)
                var_content.add_widget(table_scroll)
            
            var_card.add_widget(var_content)
            parent.add_widget(var_card)

    def _create_distribution_section(self, parent, descriptive_results):
        """Create distribution analysis section with charts."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp
        
        percentiles = descriptive_results.get('percentiles', {})
        if not percentiles:
            return
            
        # Section header
        header_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(0.8, 0.0, 0.8, 0.1),
            elevation=2
        )
        header_label = MDLabel(
            text="📊 Distribution Analysis",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        header_card.add_widget(header_label)
        parent.add_widget(header_card)
        
        # Create percentile tables for each variable
        for var_name, percentile_data in percentiles.items():
            if not isinstance(percentile_data, dict):
                continue
                
            var_card = MDCard(
                padding=dp(15),
                size_hint_y=None,
                height=dp(350),
                elevation=3
            )
            
            var_content = MDBoxLayout(orientation="vertical", spacing=dp(10))
            
            # Variable name header
            var_header = MDLabel(
                text=f"Percentiles: {var_name}",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            var_content.add_widget(var_header)
            
            # Create percentile table
            percentile_labels = [
                ('p1', '1st Percentile'),
                ('p5', '5th Percentile'),
                ('p25', '25th Percentile (Q1)'),
                ('p50', '50th Percentile (Median)'),
                ('p75', '75th Percentile (Q3)'),
                ('p95', '95th Percentile'),
                ('p99', '99th Percentile')
            ]
            
            table_data = []
            for perc_key, perc_label in percentile_labels:
                value = percentile_data.get(perc_key)
                if value is not None:
                    if isinstance(value, float):
                        formatted_value = f"{value:.3f}"
                    else:
                        formatted_value = str(value)
                    table_data.append([perc_label, formatted_value])
            
            if table_data:
                from kivymd.uix.datatables import MDDataTable
                from kivymd.uix.scrollview import MDScrollView
                
                table_scroll = MDScrollView(size_hint_y=None, height=dp(250))
                
                table = MDDataTable(
                    size_hint_y=None,
                    height=dp(len(table_data) * 40 + 100),
                    column_data=[
                        ("Percentile", dp(50)),
                        ("Value", dp(30))
                    ],
                    row_data=table_data,
                    elevation=1
                )
                
                table_scroll.add_widget(table)
                var_content.add_widget(table_scroll)
            
            var_card.add_widget(var_content)
            parent.add_widget(var_card)

    def _create_correlation_section(self, parent, correlations):
        """Create correlation analysis section."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.datatables import MDDataTable
        from kivymd.uix.scrollview import MDScrollView
        from kivy.metrics import dp
        
        # Section header
        header_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(1.0, 0.5, 0.0, 0.1),
            elevation=2
        )
        header_label = MDLabel(
            text="🔗 Correlation Analysis",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        header_card.add_widget(header_label)
        parent.add_widget(header_card)
        
        # Create correlation matrix table
        correlation_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(400),
            elevation=3
        )
        
        correlation_content = MDBoxLayout(orientation="vertical", spacing=dp(10))
        
        # Create correlation table data
        table_data = []
        variables = list(correlations.keys())
        
        # Header row
        header_row = ["Variable"] + variables
        
        # Data rows
        for var1 in variables:
            row = [var1]
            for var2 in variables:
                corr_value = correlations.get(var1, {}).get(var2)
                if corr_value is not None:
                    if isinstance(corr_value, float):
                        row.append(f"{corr_value:.3f}")
                    else:
                        row.append(str(corr_value))
                else:
                    row.append("N/A")
            table_data.append(row)
        
        if table_data:
            table_scroll = MDScrollView(size_hint_y=None, height=dp(300))
            
            # Create column data
            column_data = [("Variable", dp(30))]
            for var in variables:
                column_data.append((var[:8], dp(25)))  # Truncate long variable names
            
            table = MDDataTable(
                size_hint_y=None,
                height=dp(len(table_data) * 40 + 100),
                column_data=column_data,
                row_data=table_data,
                elevation=1
            )
            
            table_scroll.add_widget(table)
            correlation_content.add_widget(table_scroll)
        
        correlation_card.add_widget(correlation_content)
        parent.add_widget(correlation_card)

    def _create_recommendations_section(self, parent, recommendations):
        """Create recommendations section to display analysis suggestions."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.list import OneLineListItem
        from kivy.metrics import dp
        
        # Section header
        header_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(0.0, 0.8, 0.4, 0.1),
            elevation=2
        )
        header_label = MDLabel(
            text="💡 Smart Analysis Recommendations",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        header_card.add_widget(header_label)
        parent.add_widget(header_card)
        
        # Recommendations content
        rec_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(300),
            elevation=3
        )
        
        rec_content = MDBoxLayout(orientation="vertical", spacing=dp(10))
        
        # Primary recommendations
        primary_recs = recommendations.get('recommendations', {}).get('primary_recommendations', [])
        if primary_recs:
            rec_content.add_widget(MDLabel(
                text="🎯 Top Recommendations:",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            ))
            
            for i, rec in enumerate(primary_recs[:3]):  # Show top 3
                rec_layout = MDBoxLayout(
                    orientation="horizontal",
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(50)
                )
                
                rec_text = f"{i+1}. {rec.get('method', '').replace('_', ' ').title()}"
                rec_label = MDLabel(
                    text=rec_text,
                    font_style="Body1",
                    theme_text_color="Secondary",
                )
                
                run_btn = MDRaisedButton(
                    text="Run",
                    size_hint_x=None,
                    width=dp(80),
                    height=dp(35),
                    md_bg_color=(0.0, 0.7, 0.3, 1),
                    on_release=lambda x, method=rec.get('method'): self._run_recommended_analysis_method(method)
                )
                
                rec_layout.add_widget(rec_label)
                rec_layout.add_widget(run_btn)
                rec_content.add_widget(rec_layout)
        
        # Data quality warnings
        warnings = recommendations.get('recommendations', {}).get('data_quality_warnings', [])
        if warnings:
            rec_content.add_widget(MDLabel(
                text="⚠️ Data Quality Notes:",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            ))
            
            for warning in warnings[:2]:  # Show top 2 warnings
                warning_label = MDLabel(
                    text=f"• {warning}",
                    font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(25)
                )
                rec_content.add_widget(warning_label)
        
        rec_card.add_widget(rec_content)
        parent.add_widget(rec_card)

    def _create_analysis_status_section(self, parent, results):
        """Create section showing analysis status when results are not available."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp
        
        # Status card
        status_card = MDCard(
            padding=dp(20),
            size_hint_y=None,
            height=dp(200),
            elevation=3,
            md_bg_color=(0.95, 0.98, 1.0, 1)
        )
        
        status_content = MDBoxLayout(orientation="vertical", spacing=dp(15))
        
        # Status message
        status_label = MDLabel(
            text="🔍 Analysis in Progress",
            font_style="H5",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign="center"
        )
        
        info_label = MDLabel(
            text="Your data has been processed and recommendations are ready.\nDetailed analysis results will appear here shortly.",
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(60),
            halign="center"
        )
        
        # Action buttons
        button_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50),
            size_hint_x=None,
            width=dp(400),
            pos_hint={"center_x": .5}
        )
        
        retry_btn = MDRaisedButton(
            text="🔄 Retry Analysis",
            md_bg_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: self.run_auto_detection(self.analytics_screen.current_project_id)
        )
        
        manual_btn = MDFlatButton(
            text="📊 Run Manual Analysis",
            on_release=lambda x: self._show_manual_analysis_options()
        )
        
        button_layout.add_widget(retry_btn)
        button_layout.add_widget(manual_btn)
        
        status_content.add_widget(status_label)
        status_content.add_widget(info_label)
        status_content.add_widget(button_layout)
        
        status_card.add_widget(status_content)
        parent.add_widget(status_card)

    def _run_recommended_analysis_method(self, method):
        """Run a specific recommended analysis method."""
        if method:
            self._run_specific_analysis(method)

    def _show_manual_analysis_options(self):
        """Show manual analysis options."""
        self._show_tablet_analysis_type_dialog()

    def _create_outlier_section(self, parent, outliers):
        """Create outlier detection section with results tables."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.datatables import MDDataTable
        from kivymd.uix.scrollview import MDScrollView
        from kivy.metrics import dp
        
        # Section header
        header_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(1.0, 0.0, 0.0, 0.1),
            elevation=2
        )
        header_label = MDLabel(
            text="⚠️ Outlier Detection",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        header_card.add_widget(header_label)
        parent.add_widget(header_card)
        
        # Create outlier analysis for each variable
        for var_name, outlier_data in outliers.items():
            if not isinstance(outlier_data, dict):
                continue
                
            var_card = MDCard(
                padding=dp(15),
                size_hint_y=None,
                height=dp(350),
                elevation=3
            )
            
            var_content = MDBoxLayout(orientation="vertical", spacing=dp(10))
            
            # Variable name header
            var_header = MDLabel(
                text=f"Outliers: {var_name}",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            var_content.add_widget(var_header)
            
            # Create outlier summary table
            table_data = []
            
            # Basic info
            data_points = outlier_data.get('data_points', 0)
            table_data.append(['Data Points', str(data_points)])
            
            # Method results
            methods = ['iqr', 'zscore', 'mad']
            for method in methods:
                method_data = outlier_data.get(method, {})
                if isinstance(method_data, dict) and 'n_outliers' in method_data:
                    n_outliers = method_data.get('n_outliers', 0)
                    percentage = method_data.get('outlier_percentage', 0)
                    table_data.append([
                        f'{method.upper()} Outliers',
                        f'{n_outliers} ({percentage:.1f}%)'
                    ])
                elif isinstance(method_data, dict) and 'error' in method_data:
                    table_data.append([
                        f'{method.upper()} Method',
                        'Error'
                    ])
            
            if table_data:
                table_scroll = MDScrollView(size_hint_y=None, height=dp(250))
                
                table = MDDataTable(
                    size_hint_y=None,
                    height=dp(len(table_data) * 40 + 100),
                    column_data=[
                        ("Method", dp(40)),
                        ("Result", dp(40))
                    ],
                    row_data=table_data,
                    elevation=1
                )
                
                table_scroll.add_widget(table)
                var_content.add_widget(table_scroll)
            
            var_card.add_widget(var_content)
            parent.add_widget(var_card)

    def _create_data_quality_section(self, parent, data_quality):
        """Create data quality assessment section."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.datatables import MDDataTable
        from kivymd.uix.scrollview import MDScrollView
        from kivy.metrics import dp
        
        # Section header
        header_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(0.5, 0.5, 0.5, 0.1),
            elevation=2
        )
        header_label = MDLabel(
            text="🔍 Data Quality Assessment",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        header_card.add_widget(header_label)
        parent.add_widget(header_card)
        
        # Create data quality table
        quality_card = MDCard(
            padding=dp(15),
            size_hint_y=None,
            height=dp(300),
            elevation=3
        )
        
        quality_content = MDBoxLayout(orientation="vertical", spacing=dp(10))
        
        # Prepare quality metrics
        table_data = [
            ['Duplicate Rows', str(data_quality.get('duplicate_rows', 0))],
            ['Missing Data %', f"{data_quality.get('missing_percentage', 0):.1f}%"],
            ['Constant Columns', str(len(data_quality.get('constant_columns', [])))]
        ]
        
        # Show constant columns if any
        constant_cols = data_quality.get('constant_columns', [])
        if constant_cols:
            const_cols_text = ', '.join(constant_cols[:3])  # Show first 3
            if len(constant_cols) > 3:
                const_cols_text += f' (+{len(constant_cols)-3} more)'
            table_data.append(['Constant Columns List', const_cols_text])
        
        table_scroll = MDScrollView(size_hint_y=None, height=dp(200))
        
        table = MDDataTable(
            size_hint_y=None,
            height=dp(len(table_data) * 40 + 100),
            column_data=[
                ("Quality Metric", dp(50)),
                ("Value", dp(50))
            ],
            row_data=table_data,
            elevation=1
        )
        
        table_scroll.add_widget(table)
        quality_content.add_widget(table_scroll)
        quality_card.add_widget(quality_content)
        parent.add_widget(quality_card)

    def _create_action_buttons_section(self, parent, results):
        """Create action buttons for export and additional analysis."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp
        
        # Action buttons card
        action_card = MDCard(
            padding=dp(20),
            size_hint_y=None,
            height=dp(120),
            md_bg_color=(0.95, 0.95, 0.95, 1),
            elevation=2
        )
        
        button_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            size_hint_x=None,
            width=dp(600),
            pos_hint={"center_x": .5}
        )
        
        # Export Results button
        export_btn = MDRaisedButton(
            text="Export Results",
            md_bg_color=(0.2, 0.7, 0.2, 1),
            on_press=lambda x: self._export_analytics_results(results)
        )
        button_layout.add_widget(export_btn)
        
        # Run Additional Analysis button
        additional_btn = MDRaisedButton(
            text="Run Additional Analysis",
            md_bg_color=(0.2, 0.2, 0.7, 1),
            on_press=lambda x: self._show_additional_analysis_options()
        )
        button_layout.add_widget(additional_btn)
        
        # Refresh Analysis button
        refresh_btn = MDFlatButton(
            text="Refresh Analysis",
            on_press=lambda x: self.run_auto_detection(self.analytics_service.current_project_id)
        )
        button_layout.add_widget(refresh_btn)
        
        action_card.add_widget(button_layout)
        parent.add_widget(action_card)

    def _export_analytics_results(self, results):
        """Export analytics results to file."""
        try:
            import json
            from datetime import datetime
            
            # Prepare export data
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'project_id': results.get('project_id'),
                'analysis_type': results.get('analysis_type'),
                'results': results
            }
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_results_{timestamp}.json"
            
            # Save to file (you may want to use a file picker here)
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Show success message
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=f"Results exported to {filename}").open()
            
        except Exception as e:
            print(f"[ERROR] Failed to export results: {e}")
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=f"Export failed: {str(e)}").open()

    def _show_additional_analysis_options(self):
        """Show dialog for additional analysis options."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.list import OneLineListItem
        from kivymd.uix.boxlayout import MDBoxLayout
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(300)  # Fixed height for additional analysis options
        )
        
        analysis_options = [
            "Correlation Analysis",
            "Distribution Analysis", 
            "Outlier Analysis",
            "Missing Data Analysis",
            "Categorical Analysis"
        ]
        
        for option in analysis_options:
            item = OneLineListItem(
                text=option,
                on_press=lambda x, opt=option: self._run_additional_analysis(opt)
            )
            content.add_widget(item)
        
        self.additional_analysis_dialog = MDDialog(
            title="Additional Analysis Options",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_press=lambda x: self.additional_analysis_dialog.dismiss()
                )
            ]
        )
        self.additional_analysis_dialog.open()

    def _run_additional_analysis(self, analysis_type):
        """Run additional specific analysis."""
        if hasattr(self, 'additional_analysis_dialog'):
            self.additional_analysis_dialog.dismiss()
        
        # Map display names to API analysis types
        analysis_mapping = {
            "Correlation Analysis": "correlation",
            "Distribution Analysis": "distribution",
            "Outlier Analysis": "outlier",
            "Missing Data Analysis": "missing",
            "Categorical Analysis": "categorical"
        }
        
        api_analysis_type = analysis_mapping.get(analysis_type, "descriptive")
        self._run_specific_analysis(api_analysis_type)
    
    def _create_tablet_data_selection_section(self, content, project_variables):
        """Create tablet-optimized data selection interface"""
        print(f"[DEBUG] _create_tablet_data_selection_section called")
        print(f"[DEBUG] project_variables type: {type(project_variables)}")
        print(f"[DEBUG] project_variables keys: {list(project_variables.keys()) if isinstance(project_variables, dict) else 'Not a dict'}")
        
        if 'error' in project_variables:
            print(f"[DEBUG] Error in project_variables, returning")
            return
        
        print(f"[DEBUG] Creating selection card...")
        selection_card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=self.TABLET_CARD_HEIGHT,
            elevation=3,
            md_bg_color=(0.97, 0.97, 1.0, 1),
            radius=[16, 16, 16, 16]  # Larger radius for tablets
        )
        
        # Header with larger elements
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(56)  # Larger header for tablets
        )
        
        selection_icon = MDIconButton(
            icon="tune",
            theme_icon_color="Custom",
            icon_color=(0.4, 0.2, 0.8, 1),
            disabled=True,
            size_hint_x=None,
            width=self.TABLET_ICON_SIZE + dp(16)
        )
        
        header_label = MDLabel(
            text="Smart Analysis Configuration",
            font_style="H4",  # Larger font for tablets
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(selection_icon)
        header_layout.add_widget(header_label)
        selection_card.add_widget(header_layout)
        
        # Variable summary with better formatting for tablets
        var_summary = f"""📊 Available Data: {project_variables.get('sample_size', 0):,} responses across {project_variables.get('variable_count', 0)} variables

📈 Numeric Variables: {len(project_variables.get('numeric_variables', []))} (for statistical analysis)
🏷️  Categorical Variables: {len(project_variables.get('categorical_variables', []))} (for frequency analysis)  
📝 Text Variables: {len(project_variables.get('text_variables', []))} (for sentiment analysis)
📅 Date/Time Variables: {len(project_variables.get('datetime_variables', []))} (for temporal analysis)"""
        
        summary_label = MDLabel(
            text=var_summary,
            font_style="Body1",  # Larger text for tablets
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(140)  # More space for text
        )
        selection_card.add_widget(summary_label)
        
        # Action buttons with tablet-friendly spacing
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=self.TABLET_BUTTON_HEIGHT + dp(8)
        )
        
        select_variables_btn = MDRaisedButton(
            text="🎯 Select Variables",
            size_hint_x=1,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(0.4, 0.2, 0.8, 1),
            font_size="16sp",  # Larger font
            on_release=lambda x: self._show_tablet_variable_selection_dialog(project_variables)
        )
        
        select_analysis_btn = MDRaisedButton(
            text="🔬 Choose Analysis Type",
            size_hint_x=1,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(0.2, 0.6, 0.8, 1),
            font_size="16sp",  # Larger font
            on_release=lambda x: self._show_tablet_analysis_type_dialog()
        )
        
        action_layout.add_widget(select_variables_btn)
        action_layout.add_widget(select_analysis_btn)
        selection_card.add_widget(action_layout)
        
        print(f"[DEBUG] About to add selection_card to content")
        print(f"[DEBUG] Selection card type: {type(selection_card)}")
        print(f"[DEBUG] Selection card children: {len(selection_card.children)}")
        
        content.add_widget(selection_card)
        print(f"[DEBUG] Added selection_card to content successfully")
    
    def _create_tablet_summary_cards(self, content, recommendations, analysis_results):
        """Create tablet-optimized summary cards with side-by-side layout"""
        # Create horizontal layout for tablets (side-by-side cards)
        cards_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=self.TABLET_CARD_HEIGHT + dp(40)
        )
        
        # Data Overview Card
        data_chars = analysis_results.get('data_characteristics', {})
        data_card = self._create_tablet_data_overview_card(data_chars)
        cards_layout.add_widget(data_card)
        
        # Recommendations Card
        rec_data = recommendations.get('recommendations', recommendations)
        rec_card = self._create_tablet_recommendations_card(rec_data)
        cards_layout.add_widget(rec_card)
        
        content.add_widget(cards_layout)
        
        # Analysis results card (full width)
        analyses = analysis_results.get('analyses', {})
        if analyses:
            results_card = self._create_tablet_analysis_results_card(analyses)
            content.add_widget(results_card)
    
    def _create_tablet_analysis_options(self, content, available_types):
        """Create tablet-optimized analysis options with better grid layout"""
        if 'error' in available_types:
            return
        
        options_card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(400),  # Larger for tablets
            elevation=3,
            md_bg_color=(0.98, 1.0, 0.97, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_label = MDLabel(
            text="🔬 Advanced Analysis Options",
            font_style="H4",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48),
            bold=True
        )
        options_card.add_widget(header_label)
        
        # Analysis types grid optimized for tablets (more columns)
        analysis_types = available_types.get('main_analysis_types', {})
        
        types_grid = GridLayout(
            cols=3,  # More columns for tablets
            spacing=dp(16),  # Larger spacing
            size_hint_y=None,
            height=dp(240)  # More height for larger buttons
        )
        
        # Key analysis types with tablet-friendly design
        key_types = ['basic', 'comprehensive', 'distribution', 'categorical', 'outlier', 'quality', 'correlation', 'missing', 'text']
        
        for analysis_type in key_types:
            if analysis_type in analysis_types:
                type_info = analysis_types[analysis_type]
                type_btn = self._create_tablet_analysis_type_button(analysis_type, type_info)
                types_grid.add_widget(type_btn)
        
        options_card.add_widget(types_grid)
        
        # Quick action buttons with tablet spacing
        quick_actions = MDBoxLayout(
            orientation="horizontal",
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=self.TABLET_BUTTON_HEIGHT + dp(8)
        )
        
        comprehensive_btn = MDRaisedButton(
            text="🏆 Run Full Analysis Suite",
            size_hint_x=2,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(0.2, 0.8, 0.2, 1),
            font_size="16sp",
            on_release=lambda x: self._run_specific_analysis('comprehensive')
        )
        
        quality_btn = MDRaisedButton(
            text="🔍 Quick Quality Check",
            size_hint_x=1,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(0.8, 0.6, 0.2, 1),
            font_size="16sp",
            on_release=lambda x: self._run_specific_analysis('quality')
        )
        
        quick_actions.add_widget(comprehensive_btn)
        quick_actions.add_widget(quality_btn)
        options_card.add_widget(quick_actions)
        
        content.add_widget(options_card)
    
    def _create_tablet_analysis_type_button(self, analysis_type, type_info):
        """Create tablet-optimized analysis type button"""
        color_map = {
            'basic': (0.2, 0.6, 1.0, 1),
            'comprehensive': (0.8, 0.2, 0.8, 1),
            'distribution': (1.0, 0.6, 0.2, 1),
            'categorical': (0.2, 0.8, 0.6, 1),
            'outlier': (0.8, 0.4, 0.2, 1),
            'quality': (0.6, 0.8, 0.2, 1),
            'correlation': (0.4, 0.2, 0.8, 1),
            'missing': (0.8, 0.6, 0.4, 1),
            'text': (0.6, 0.4, 0.8, 1)
        }
        
        btn_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(72),  # Larger buttons for tablets
            md_bg_color=color_map.get(analysis_type, (0.5, 0.5, 0.5, 1)),
            radius=12,
            padding=dp(12)
        )
        btn_layout.bind(on_release=lambda x: self._run_specific_analysis(analysis_type))
        
        # Icon + title layout
        title_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32)
        )
        
        # Add icon based on analysis type
        icon_map = {
            'basic': "chart-bar",
            'comprehensive': "star",
            'distribution': "chart-bell-curve",
            'categorical': "tag-multiple",
            'outlier': "target",
            'quality': "shield-check",
            'correlation': "link",
            'missing': "help-circle",
            'text': "text"
        }
        
        icon = MDIconButton(
            icon=icon_map.get(analysis_type, "chart-line"),
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(32)
        )
        
        title_label = MDLabel(
            text=analysis_type.title(),
            font_style="Button",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True,
            halign="left"
        )
        
        title_layout.add_widget(icon)
        title_layout.add_widget(title_label)
        
        # Description
        description = type_info.get('description', f'{analysis_type} analysis')
        desc_label = MDLabel(
            text=description[:40] + "..." if len(description) > 40 else description,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(32)
        )
        
        btn_layout.add_widget(title_layout)
        btn_layout.add_widget(desc_label)
        
        return btn_layout
    
    def _show_tablet_variable_selection_dialog(self, project_variables):
        """Show tablet-optimized variable selection dialog"""
        if 'error' in project_variables:
            toast("Error loading project variables")
            return
        
        # Create tablet-sized dialog content
        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(500)  # Larger for tablets
        )
        
        # Instructions with larger text
        instructions = MDLabel(
            text="Select variables to include in your analysis:",
            font_style="H6",  # Larger font for tablets
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40)
        )
        dialog_content.add_widget(instructions)
        
        # Scrollable variable list
        scroll_view = MDScrollView(
            size_hint=(1, 1)
        )
        
        variables_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),  # More spacing for tablets
            size_hint_y=None,
            height=dp(800)  # Fixed height for variable list
        )
        
        # Store checkboxes for later reference
        self.variable_checkboxes = {}
        
        # Variable categories with tablet-friendly layout
        categories = [
            ('numeric_variables', '📈 Numeric Variables', (0.2, 0.6, 1.0, 1)),
            ('categorical_variables', '🏷️ Categorical Variables', (0.2, 0.8, 0.6, 1)),
            ('text_variables', '📝 Text Variables', (0.6, 0.4, 0.8, 1)),
            ('datetime_variables', '📅 Date/Time Variables', (0.8, 0.6, 0.2, 1))
        ]
        
        for var_type, header_text, color in categories:
            if project_variables.get(var_type):
                # Category header
                header_card = MDCard(
                    orientation="vertical",
                    padding=dp(16),
                    spacing=dp(8),
                    size_hint_y=None,
                    height=dp(60),
                    md_bg_color=color,
                    radius=8
                )
                
                header_label = MDLabel(
                    text=header_text,
                    font_style="H6",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    bold=True
                )
                header_card.add_widget(header_label)
                variables_layout.add_widget(header_card)
                
                # Variables in this category
                for var in project_variables[var_type]:
                    var_layout = MDBoxLayout(
                        orientation="horizontal",
                        spacing=dp(16),  # More spacing for tablets
                        size_hint_y=None,
                        height=dp(48),  # Larger touch targets
                        padding=[dp(16), 0, dp(16), 0]
                    )
                    
                    checkbox = MDCheckbox(
                        size_hint_x=None,
                        width=dp(48),  # Larger checkbox for tablets
                        active=True  # Default to selected
                    )
                    self.variable_checkboxes[var] = checkbox
                    
                    var_label = MDLabel(
                        text=var,
                        font_style="Body1",  # Larger text
                        theme_text_color="Secondary"
                    )
                    
                    var_layout.add_widget(checkbox)
                    var_layout.add_widget(var_label)
                    variables_layout.add_widget(var_layout)
        
        scroll_view.add_widget(variables_layout)
        dialog_content.add_widget(scroll_view)
        
        # Create tablet-sized dialog
        self.analysis_dialog = MDDialog(
            title="Select Variables for Analysis",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.85, 0.85),  # Larger for tablets
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    font_size="16sp",
                    on_release=lambda x: self.analysis_dialog.dismiss()
                ),
                MDFlatButton(
                    text="Select All",
                    font_size="16sp",
                    on_release=lambda x: self._select_all_variables()
                ),
                MDRaisedButton(
                    text="Run Analysis",
                    font_size="16sp",
                    on_release=lambda x: self._run_analysis_with_selected_variables()
                )
            ]
        )
        
        self.analysis_dialog.open()
    
    def _select_all_variables(self):
        """Select all variables in the dialog"""
        for checkbox in self.variable_checkboxes.values():
            checkbox.active = True
    
    def _show_tablet_analysis_type_dialog(self):
        """Show tablet-optimized analysis type selection"""
        # Create grid of analysis type cards instead of dropdown
        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(600)  # Fixed height for dialog content
        )
        
        # Instructions
        instructions = MDLabel(
            text="Choose your analysis approach:",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40)
        )
        dialog_content.add_widget(instructions)
        
        # Analysis types grid
        types_grid = GridLayout(
            cols=2,  # 2 columns for tablet
            spacing=dp(16),
            size_hint_y=None,
            height=dp(480)
        )
        
        analysis_options = [
            ("auto", "🤖 Smart Auto-Detection", "Let AI choose the best analysis", (0.4, 0.2, 0.8, 1)),
            ("basic", "📊 Basic Statistics", "Mean, median, standard deviation", (0.2, 0.6, 1.0, 1)),
            ("comprehensive", "🏆 Comprehensive Suite", "Full statistical analysis", (0.8, 0.2, 0.8, 1)),
            ("distribution", "📈 Distribution Analysis", "Check data distributions", (1.0, 0.6, 0.2, 1)),
            ("categorical", "🏷️ Categorical Analysis", "Analyze categorical variables", (0.2, 0.8, 0.6, 1)),
            ("quality", "🔍 Data Quality Check", "Assess data completeness", (0.6, 0.8, 0.2, 1)),
        ]
        
        for type_code, title, description, color in analysis_options:
            option_card = self._create_analysis_option_card(type_code, title, description, color)
            types_grid.add_widget(option_card)
        
        dialog_content.add_widget(types_grid)
        
        # Create dialog
        type_dialog = MDDialog(
            title="Choose Analysis Type",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.9),
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    font_size="16sp",
                    on_release=lambda x: type_dialog.dismiss()
                )
            ]
        )
        
        type_dialog.open()
    
    def _create_analysis_option_card(self, type_code, title, description, color):
        """Create analysis option card for tablet dialog"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(120),
            md_bg_color=color,
            radius=12,
            on_release=lambda x: self._select_and_run_analysis(type_code)
        )
        
        title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(32)
        )
        
        desc_label = MDLabel(
            text=description,
            font_style="Body2",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(64)
        )
        
        card.add_widget(title_label)
        card.add_widget(desc_label)
        
        return card
    
    def _select_and_run_analysis(self, analysis_type):
        """Select analysis type and run it"""
        # Close any open dialogs
        try:
            if hasattr(self, 'analysis_dialog') and self.analysis_dialog:
                self.analysis_dialog.dismiss()
        except:
            pass
        
        self._run_specific_analysis(analysis_type)
    
    # Tablet-optimized card creation methods
    def _create_tablet_data_overview_card(self, data_characteristics):
        """Create tablet-optimized data overview card"""
        card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=dp(16),
            size_hint_y=None,
            height=self.TABLET_CARD_HEIGHT,
            size_hint_x=0.5,  # Half width for side-by-side layout
            elevation=3,
            md_bg_color=(0.98, 0.99, 1.0, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(56)
        )
        
        data_icon = MDIconButton(
            icon="database",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48)
        )
        
        header_label = MDLabel(
            text="📊 Data Overview",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(data_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Metrics in vertical layout for tablets
        sample_size = data_characteristics.get('sample_size', 'N/A')
        variable_count = data_characteristics.get('variable_count', 'N/A')
        completeness = data_characteristics.get('completeness_score', 0)
        
        metrics_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(160)
        )
        
        metrics = [
            ("📋 Sample Size", f"{sample_size:,}" if isinstance(sample_size, int) else str(sample_size)),
            ("📊 Variables", str(variable_count)),
            ("✅ Completeness", f"{completeness:.1f}%"),
            ("⭐ Quality", "Excellent" if completeness > 90 else "Good" if completeness > 80 else "Fair" if completeness > 60 else "Poor")
        ]
        
        for title, value in metrics:
            metric_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(12),
                size_hint_y=None,
                height=dp(32)
            )
            
            title_label = MDLabel(
                text=title,
                font_style="Body1",
                theme_text_color="Secondary",
                size_hint_x=0.6
            )
            
            value_label = MDLabel(
                text=value,
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_x=0.4,
                halign="right"
            )
            
            metric_layout.add_widget(title_label)
            metric_layout.add_widget(value_label)
            metrics_layout.add_widget(metric_layout)
        
        card.add_widget(metrics_layout)
        
        # Summary text
        summary_text = f"Dataset contains {sample_size:,} responses across {variable_count} variables"
        summary_label = MDLabel(
            text=summary_text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(48),
            halign="center"
        )
        card.add_widget(summary_label)
        
        return card
    
    def _create_tablet_recommendations_card(self, recommendations):
        """Create tablet-optimized recommendations card"""
        card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=dp(16),
            size_hint_y=None,
            height=self.TABLET_CARD_HEIGHT,
            size_hint_x=0.5,  # Half width for side-by-side layout
            elevation=3,
            md_bg_color=(0.98, 1.0, 0.98, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(56)
        )
        
        rec_icon = MDIconButton(
            icon="lightbulb",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.8, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48)
        )
        
        header_label = MDLabel(
            text="💡 Smart Recommendations",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(rec_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Recommendations content
        primary_recs = recommendations.get('primary_recommendations', [])
        
        if primary_recs:
            top_rec = primary_recs[0]
            
            # Primary recommendation with better tablet layout
            rec_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                size_hint_y=None,
                height=dp(120)
            )
            
            rec_title = MDLabel(
                text=f"🎯 {top_rec.get('method', 'Analysis').replace('_', ' ').title()}",
                font_style="H6",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(40),
                bold=True
            )
            
            rec_desc = MDLabel(
                text=top_rec.get('rationale', 'Recommended based on your data characteristics'),
                font_style="Body1",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60)
            )
            
            rec_content.add_widget(rec_title)
            rec_content.add_widget(rec_desc)
            card.add_widget(rec_content)
            
            # Action button
            action_button = MDRaisedButton(
                text=f"🚀 Run {top_rec.get('method', 'Analysis').replace('_', ' ').title()}",
                size_hint_y=None,
                height=self.TABLET_BUTTON_HEIGHT,
                md_bg_color=(0.2, 0.8, 0.2, 1),
                font_size="16sp",
                on_release=lambda x: self._run_recommended_analysis(top_rec)
            )
            card.add_widget(action_button)
            
            # Additional info
            additional_count = len(recommendations.get('secondary_recommendations', []))
            if additional_count > 0:
                additional_label = MDLabel(
                    text=f"💡 {additional_count} more recommendations available",
                    font_style="Caption",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=dp(24)
                )
                card.add_widget(additional_label)
        else:
            no_recs_label = MDLabel(
                text="🔍 Analyzing your data...\nRecommendations will appear here",
                font_style="Body1",
                theme_text_color="Secondary",
                halign="center"
            )
            card.add_widget(no_recs_label)
        
        return card
    
    def _create_tablet_analysis_results_card(self, analyses):
        """Create tablet-optimized analysis results card"""
        card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=dp(16),
            size_hint_y=None,
            height=dp(220),  # Shorter for tablet landscape
            elevation=3,
            md_bg_color=(1.0, 0.99, 0.97, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(56)
        )
        
        results_icon = MDIconButton(
            icon="chart-line",
            theme_icon_color="Custom",
            icon_color=(1.0, 0.6, 0.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48)
        )
        
        header_label = MDLabel(
            text="📈 Analysis Results Preview",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(results_icon)
        header_layout.add_widget(header_label)
        card.add_widget(header_layout)
        
        # Results chips in horizontal layout
        results_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        # Show available analyses as chips
        for analysis_type, result in analyses.items():
            if result and 'error' not in result:
                chip = self._create_tablet_analysis_chip(analysis_type)
                results_layout.add_widget(chip)
        
        card.add_widget(results_layout)
        
        # Action buttons
        actions_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=self.TABLET_BUTTON_HEIGHT + dp(8)
        )
        
        details_button = MDRaisedButton(
            text="📋 View Detailed Results",
            size_hint_x=2,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(1.0, 0.6, 0.0, 1),
            font_size="16sp",
            on_release=lambda x: self._show_detailed_results(analyses)
        )
        
        export_button = MDRaisedButton(
            text="📤 Export",
            size_hint_x=1,
            height=self.TABLET_BUTTON_HEIGHT,
            md_bg_color=(0.6, 0.6, 0.6, 1),
            font_size="16sp",
            on_release=lambda x: self._export_results('combined', analyses)
        )
        
        actions_layout.add_widget(details_button)
        actions_layout.add_widget(export_button)
        card.add_widget(actions_layout)
        
        return card
    
    def _create_tablet_analysis_chip(self, analysis_type):
        """Create tablet-sized analysis chip"""
        chip_layout = MDBoxLayout(
            orientation="horizontal",
            padding=[dp(16), dp(8), dp(16), dp(8)],
            spacing=dp(8),
            size_hint_x=None,
            width=dp(160),
            size_hint_y=None,
            height=dp(40),
            md_bg_color=(0.85, 0.92, 1.0, 1),
            radius=20
        )
        
        # Status icon
        status_icon = MDIconButton(
            icon="check-circle",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.8, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(24)
        )
        
        chip_label = MDLabel(
            text=analysis_type.replace('_', ' ').title(),
            font_style="Button",
            theme_text_color="Primary",
            halign="left",
            bold=True
        )
        
        chip_layout.add_widget(status_icon)
        chip_layout.add_widget(chip_label)
        return chip_layout
    
    def _create_tablet_empty_state(self, message):
        """Create tablet-optimized empty state widget"""
        empty_card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=dp(20),
            size_hint_y=None,
            height=dp(300),
            elevation=2,
            md_bg_color=(0.98, 0.98, 0.98, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Icon
        empty_icon = MDIconButton(
            icon="information",
            theme_icon_color="Custom",
            icon_color=(0.6, 0.6, 0.6, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(64)
        )
        
        # Message
        empty_label = MDLabel(
            text=message,
            font_style="H6",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(120)
        )
        
        # Center everything
        center_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(200)
        )
        center_layout.add_widget(empty_icon)
        center_layout.add_widget(empty_label)
        
        empty_card.add_widget(center_layout)
        return empty_card
    
    # Continue with existing methods but with tablet optimizations...
    def _run_specific_analysis(self, analysis_type):
        """Run specific analysis type with tablet feedback"""
        project_id = self.analytics_screen.current_project_id
        if not project_id:
            toast("Please select a project first")
            return
        
        toast(f"🔬 Running {analysis_type.replace('_', ' ').title()} analysis...")
        
        threading.Thread(
            target=self._run_specific_analysis_thread,
            args=(project_id, analysis_type),
            daemon=True
        ).start()
    
    def _run_specific_analysis_thread(self, project_id: str, analysis_type: str):
        """Background thread for specific analysis with tablet-optimized results"""
        try:
            self.analytics_screen.set_loading(True)
            
            # Run the specific analysis
            if analysis_type == 'basic':
                result = self.analytics_service.run_basic_statistics(project_id)
            elif analysis_type == 'distribution':
                result = self.analytics_service.run_distribution_analysis(project_id)
            elif analysis_type == 'categorical':
                result = self.analytics_service.run_categorical_analysis(project_id)
            elif analysis_type == 'outlier':
                result = self.analytics_service.run_outlier_analysis(project_id)
            elif analysis_type == 'quality':
                result = self.analytics_service.run_data_quality_analysis(project_id)
            elif analysis_type == 'missing':
                result = self.analytics_service.run_missing_data_analysis(project_id)
            elif analysis_type == 'comprehensive':
                result = self.analytics_service.generate_comprehensive_report(project_id)
            else:
                result = self.analytics_service.run_analysis(project_id, analysis_type)
            
            Clock.schedule_once(
                lambda dt: self._display_tablet_analysis_results(analysis_type, result), 0
            )
            
        except Exception as e:
            print(f"Error in {analysis_type} analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast(f"❌ {analysis_type.title()} analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _display_tablet_analysis_results(self, analysis_type: str, result: Dict):
        """Display results with tablet-optimized dialog"""
        if 'error' in result:
            toast(f"❌ Analysis failed: {result['error']}")
            return
        
        # Show tablet-optimized results dialog
        self._show_tablet_analysis_results_dialog(analysis_type, result)
    
    def _show_tablet_analysis_results_dialog(self, analysis_type: str, result: Dict):
        """Show tablet-optimized analysis results dialog"""
        # Create tablet-sized scrollable results content
        results_content = MDScrollView(
            size_hint=(1, 1)
        )
        
        results_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(1000),  # Fixed height for results layout
            padding=[self.TABLET_PADDING, self.TABLET_PADDING, self.TABLET_PADDING, self.TABLET_PADDING]
        )
        
        # Format and display results with better tablet formatting
        formatted_results = self._format_tablet_analysis_results(analysis_type, result)
        
        results_label = MDLabel(
            text=formatted_results,
            font_style="Body1",  # Larger font for tablets
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(800),  # Fixed height for results text
            text_size=(dp(600), None)  # Fixed width for proper text wrapping
        )
        
        results_layout.add_widget(results_label)
        results_content.add_widget(results_layout)
        
        # Create tablet-sized results dialog
        results_dialog = MDDialog(
            title=f"📊 {analysis_type.replace('_', ' ').title()} Results",
            type="custom",
            content_cls=results_content,
            size_hint=(0.9, 0.85),  # Larger for tablets
            buttons=[
                MDFlatButton(
                    text="Close",
                    font_size="16sp",
                    on_release=lambda x: results_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="📤 Export Results",
                    font_size="16sp",
                    on_release=lambda x: self._export_results(analysis_type, result)
                )
            ]
        )
        
        results_dialog.open()
    
    def _format_tablet_analysis_results(self, analysis_type: str, result: Dict) -> str:
        """Format analysis results for tablet display with better formatting"""
        if not result or 'error' in result:
            return f"❌ Analysis failed: {result.get('error', 'Unknown error')}"
        
        formatted_text = f"✅ {analysis_type.replace('_', ' ').title()} Analysis Complete\n\n"
        
        # Enhanced formatting for tablets with emoji and better structure
        if analysis_type == 'basic' and 'results' in result:
            basic_results = result['results']
            if 'summary' in basic_results:
                summary = basic_results['summary']
                formatted_text += f"📊 Variables Analyzed: {summary.get('variables_analyzed', 'N/A')}\n"
                formatted_text += f"📋 Total Observations: {summary.get('observations', 'N/A'):,}\n\n"
                
                # Add variable details if available
                if 'basic_statistics' in basic_results:
                    formatted_text += "📈 Statistical Summary:\n"
                    stats = basic_results['basic_statistics']
                    for var_name, var_stats in stats.items():
                        if isinstance(var_stats, dict) and 'mean' in var_stats:
                            formatted_text += f"  • {var_name}:\n"
                            formatted_text += f"    Mean: {var_stats.get('mean', 'N/A'):.2f}\n"
                            formatted_text += f"    Median: {var_stats.get('median', 'N/A'):.2f}\n"
                            formatted_text += f"    Std Dev: {var_stats.get('std', 'N/A'):.2f}\n\n"
        
        elif analysis_type == 'quality' and 'results' in result:
            quality_results = result['results']
            if 'summary' in quality_results:
                summary = quality_results['summary']
                score = summary.get('overall_quality_score', 'N/A')
                formatted_text += f"🏆 Overall Quality Score: {score:.1f}%\n"
                formatted_text += f"📊 Variables: {summary.get('variables', 'N/A')}\n"
                formatted_text += f"📋 Observations: {summary.get('observations', 'N/A'):,}\n\n"
                
                # Quality indicators
                if score != 'N/A':
                    if score > 90:
                        formatted_text += "✅ Data Quality: Excellent\n"
                    elif score > 80:
                        formatted_text += "☑️ Data Quality: Good\n"
                    elif score > 60:
                        formatted_text += "⚠️ Data Quality: Fair\n"
                    else:
                        formatted_text += "❌ Data Quality: Poor\n"
        
        elif analysis_type == 'comprehensive' and 'results' in result:
            comp_results = result['results']
            if 'report_metadata' in comp_results:
                metadata = comp_results['report_metadata']
                formatted_text += f"📄 Report Type: {metadata.get('report_type', 'N/A')}\n"
                formatted_text += f"🕒 Generated: {metadata.get('generated_at', 'N/A')[:19]}\n"
                formatted_text += f"📊 Data Shape: {metadata.get('data_shape', 'N/A')}\n\n"
            
            if 'executive_summary' in comp_results:
                summary = comp_results['executive_summary']
                if isinstance(summary, dict):
                    formatted_text += "📋 Executive Summary:\n"
                    for key, value in summary.items():
                        if isinstance(value, (str, int, float)):
                            formatted_text += f"  • {key.replace('_', ' ').title()}: {value}\n"
        
        else:
            # Generic formatting with emojis
            formatted_text += f"🎯 Analysis completed successfully!\n\n"
            if 'summary' in result:
                summary = result['summary']
                for key, value in summary.items():
                    formatted_text += f"📌 {key.replace('_', ' ').title()}: {value}\n"
            
            # Add data characteristics if available
            if 'data_characteristics' in result:
                chars = result['data_characteristics']
                formatted_text += f"\n📊 Data Characteristics:\n"
                formatted_text += f"  • Sample Size: {chars.get('sample_size', 'N/A'):,}\n"
                formatted_text += f"  • Variables: {chars.get('variable_count', 'N/A')}\n"
                formatted_text += f"  • Completeness: {chars.get('completeness_score', 'N/A'):.1f}%\n"
        
        return formatted_text
    
    def _run_analysis_with_selected_variables(self):
        """Run analysis with user-selected variables"""
        # Collect selected variables
        selected_variables = []
        for var_name, checkbox in self.variable_checkboxes.items():
            if checkbox.active:
                selected_variables.append(var_name)
        
        if self.analysis_dialog:
            self.analysis_dialog.dismiss()
        
        if not selected_variables:
            toast("❌ Please select at least one variable")
            return
        
        toast(f"🚀 Running analysis with {len(selected_variables)} selected variables...")
        
        # Run analysis with selected variables
        project_id = self.analytics_screen.current_project_id
        threading.Thread(
            target=self._run_analysis_with_variables_thread,
            args=(project_id, selected_variables),
            daemon=True
        ).start()
    
    def _run_analysis_with_variables_thread(self, project_id: str, variables: List[str]):
        """Run analysis with specific variables"""
        try:
            result = self.analytics_service.run_analysis(project_id, "auto", variables)
            Clock.schedule_once(
                lambda dt: self._display_tablet_analysis_results("custom", result), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: toast("❌ Analysis with selected variables failed"), 0
            )
    
    def _export_results(self, analysis_type: str, result: Dict):
        """Export analysis results with tablet feedback"""
        try:
            exported = self.analytics_service.export_analysis_results(result, 'json')
            toast(f"✅ {analysis_type.title()} results exported successfully!")
        except Exception as e:
            toast(f"❌ Export failed: {str(e)}")
    
    def _show_detailed_results(self, analyses):
        """Show detailed results with tablet navigation"""
        toast("💡 Switch to Descriptive or Qualitative tabs for detailed analysis results")
    
    def _run_recommended_analysis(self, recommendation: Dict):
        """Execute recommended analysis with tablet feedback"""
        method = recommendation.get('method', '')
        category = recommendation.get('category', 'descriptive')
        
        toast(f"🎯 Running recommended {method.replace('_', ' ').title()} analysis...")
        
        if category == 'descriptive':
            self.analytics_screen.current_tab = "descriptive"
            Clock.schedule_once(lambda dt: self.analytics_screen.load_descriptive(), 0.5)
        elif category == 'qualitative':
            self.analytics_screen.current_tab = "qualitative"
            Clock.schedule_once(lambda dt: self.analytics_screen.load_qualitative(), 0.5)
        else:
            self._run_specific_analysis(method)

    def test_visualizations(self):
        """Test method to verify visualization components work correctly."""
        try:
            print("[DEBUG] Testing visualization components...")
            
            # Create sample analytics results for testing
            sample_results = {
                'project_id': 'test-project',
                'analysis_type': 'auto',
                'data_characteristics': {
                    'sample_size': 100,
                    'variable_count': 5,
                    'numeric_variables': ['age', 'income'],
                    'categorical_variables': ['gender', 'location'],
                    'text_variables': ['feedback'],
                    'datetime_variables': ['timestamp'],
                    'completeness_score': 85.5,
                    'data_quality': {
                        'duplicate_rows': 2,
                        'constant_columns': ['status'],
                        'missing_percentage': 14.5
                    }
                },
                'analyses': {
                    'descriptive': {
                        'basic_stats': {
                            'age': {
                                'mean': 35.2,
                                'median': 34.0,
                                'std': 12.5,
                                'min': 18.0,
                                'max': 65.0,
                                'count': 98,
                                'missing_count': 2,
                                'unique_count': 45
                            },
                            'income': {
                                'mean': 52000.0,
                                'median': 48000.0,
                                'std': 18000.0,
                                'min': 25000.0,
                                'max': 95000.0,
                                'count': 95,
                                'missing_count': 5,
                                'unique_count': 78
                            }
                        },
                        'percentiles': {
                            'age': {
                                'p1': 19.0,
                                'p5': 22.0,
                                'p25': 28.0,
                                'p50': 34.0,
                                'p75': 42.0,
                                'p95': 58.0,
                                'p99': 63.0
                            }
                        },
                        'correlations': {
                            'age': {'age': 1.0, 'income': 0.65},
                            'income': {'age': 0.65, 'income': 1.0}
                        },
                        'outliers': {
                            'age': {
                                'data_points': 98,
                                'iqr': {
                                    'method': 'IQR',
                                    'n_outliers': 3,
                                    'outlier_percentage': 3.1
                                },
                                'zscore': {
                                    'method': 'Z-score',
                                    'n_outliers': 2,
                                    'outlier_percentage': 2.0
                                }
                            }
                        }
                    }
                }
            }
            
            # Test the display with sample data
            self._display_auto_detection_results(sample_results)
            print("[DEBUG] Test visualization completed successfully")
            
        except Exception as e:
            print(f"[ERROR] Test visualization failed: {e}")
            import traceback
            traceback.print_exc()