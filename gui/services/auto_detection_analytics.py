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
from kivymd.uix.scrollview import MDScrollView  # FIXED: Added missing import
from kivymd.uix.selectioncontrol import MDCheckbox  # Added for variable selection
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
import threading
from kivy.clock import Clock
from kivymd.toast import toast


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
            print(f"[DEBUG] Recommendations result: {recommendations}")
            
            # Run comprehensive auto analysis
            print(f"[DEBUG] Running auto analysis...")
            analysis_results = self.analytics_service.run_analysis(project_id, "auto")
            print(f"[DEBUG] Analysis results: {analysis_results}")
            
            # Get available analysis types
            print(f"[DEBUG] Getting available analysis types...")
            available_types = self.analytics_service.get_available_analysis_types()
            print(f"[DEBUG] Available types result: {available_types}")
            
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
        """Display enhanced auto-detection results with tablet-optimized layout"""
        print(f"[DEBUG] _display_auto_detection_results called")
        print(f"[DEBUG] Results type: {type(results)}")
        print(f"[DEBUG] Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        # Use the helper method to get the content area
        content = self.analytics_screen.get_tab_content('auto_detection')
        
        if not content:
            print(f"[DEBUG] ERROR: Could not get auto_detection content area")
            return
            
        content.clear_widgets()
        print(f"[DEBUG] Content widget cleared, type: {type(content)}")
        
        # Add a simple test widget first to verify the basic setup
        from kivymd.uix.label import MDLabel
        test_label = MDLabel(
            text="🧪 TEST: Auto-detection results loading...",
            font_style="H6",
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(test_label)
        print(f"[DEBUG] Added test label, content children: {len(content.children)}")
        
        # Add a small delay before continuing to ensure the test label is visible
        Clock.schedule_once(lambda dt: self._continue_display_results(content, results, test_label), 0.5)
        
    def _continue_display_results(self, content, results, test_label):
        """Continue displaying results after test label delay"""
        print(f"[DEBUG] _continue_display_results called")
        print(f"[DEBUG] Content type: {type(content)}")
        print(f"[DEBUG] Content children before: {len(content.children)}")
        print(f"[DEBUG] Results type: {type(results)}")
        print(f"[DEBUG] Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        # Remove test label
        if test_label in content.children:
            content.remove_widget(test_label)
            print(f"[DEBUG] Removed test label, children now: {len(content.children)}")
        else:
            print(f"[DEBUG] Test label not in content.children")
        
        # Now create the actual analytics content
        if not results:
            print(f"[DEBUG] No results provided, showing empty state")
            empty_widget = self._create_tablet_empty_state(
                "No analysis recommendations available.\nPlease ensure the FastAPI backend is running."
            )
            content.add_widget(empty_widget)
            print(f"[DEBUG] Added empty state widget, content children count: {len(content.children)}")
            return
        
        recommendations = results.get('recommendations', {})
        analysis_results = results.get('analysis_results', {})
        project_variables = results.get('project_variables', {})
        
        print(f"[DEBUG] Processing results - recommendations type: {type(recommendations)}")
        print(f"[DEBUG] Processing results - analysis_results type: {type(analysis_results)}")
        print(f"[DEBUG] Processing results - project_variables type: {type(project_variables)}")
        
        # Check for errors
        if 'error' in recommendations or 'error' in analysis_results:
            error_msg = recommendations.get('error') or analysis_results.get('error')
            print(f"[DEBUG] Error found: {error_msg}")
            if 'Cannot connect to analytics backend' in str(error_msg):
                content.add_widget(self.analytics_screen.create_backend_error_widget())
            else:
                content.add_widget(self._create_tablet_empty_state(f"Error: {error_msg}"))
            return
        
        print(f"[DEBUG] Creating fixed-height analytics interface...")
        
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        # 1. Data Overview Card (Fixed Height)
        data_overview_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(220),  # Fixed height
            padding=dp(20),
            spacing=dp(12),
            md_bg_color=(0.98, 0.99, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        data_icon = MDIconButton(
            icon="chart-box",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48),
            user_font_size="24sp"
        )
        
        header_label = MDLabel(
            text="📊 Data Overview",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(data_icon)
        header_layout.add_widget(header_label)
        data_overview_card.add_widget(header_layout)
        
        # Data metrics
        sample_size = project_variables.get('sample_size', 'N/A')
        variable_count = project_variables.get('variable_count', 'N/A')
        
        metrics_text = f"""📋 Sample Size: {sample_size:,} responses
📊 Variables: {variable_count} total variables
📈 Numeric: {len(project_variables.get('numeric_variables', []))}
🏷️ Categorical: {len(project_variables.get('categorical_variables', []))}
📝 Text: {len(project_variables.get('text_variables', []))}
📅 Date/Time: {len(project_variables.get('datetime_variables', []))}"""
        
        metrics_label = MDLabel(
            text=metrics_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(120)
        )
        data_overview_card.add_widget(metrics_label)
        
        content.add_widget(data_overview_card)
        print(f"[DEBUG] Added data overview card")
        
        # 2. Recommendations Card (Fixed Height)
        recommendations_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(280),  # Increased height
            padding=dp(20),
            spacing=dp(12),
            md_bg_color=(0.98, 1.0, 0.98, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Recommendations header
        rec_header = MDLabel(
            text="💡 Smart Recommendations",
            font_style="H5",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(32)
        )
        recommendations_card.add_widget(rec_header)
        
        # Primary recommendation
        primary_recs = recommendations.get('recommendations', {}).get('primary_recommendations', [])
        if primary_recs:
            top_rec = primary_recs[0]
            rec_text = f"""🎯 Recommended: {top_rec.get('method', 'Analysis').replace('_', ' ').title()}
            
📋 {top_rec.get('rationale', 'Recommended based on your data characteristics')}

✨ {len(primary_recs)} analysis recommendations available"""
        else:
            rec_text = "🔍 Analyzing your data for recommendations..."
        
        rec_content = MDLabel(
            text=rec_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(140)
        )
        recommendations_card.add_widget(rec_content)
        
        # Action button
        if primary_recs:
            action_button = MDRaisedButton(
                text=f"🚀 Run {primary_recs[0].get('method', 'Analysis').replace('_', ' ').title()}",
                size_hint_y=None,
                height=dp(48),
                md_bg_color=(0.2, 0.8, 0.2, 1),
                font_size="16sp"
            )
            recommendations_card.add_widget(action_button)
        
        content.add_widget(recommendations_card)
        print(f"[DEBUG] Added recommendations card")
        
        # 3. Quick Analysis Options (Fixed Height)
        options_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(180),  # Fixed height
            padding=dp(20),
            spacing=dp(12),
            md_bg_color=(1.0, 0.99, 0.97, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        options_header = MDLabel(
            text="🔬 Quick Analysis Options",
            font_style="H5",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(32)
        )
        options_card.add_widget(options_header)
        
        # Analysis buttons in horizontal layout
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        analysis_options = [
            ("📊 Basic Stats", "basic", (0.2, 0.6, 1.0, 1)),
            ("📈 Distributions", "distribution", (1.0, 0.6, 0.2, 1)),
            ("🏷️ Categorical", "categorical", (0.2, 0.8, 0.6, 1)),
            ("🔍 Quality Check", "quality", (0.6, 0.8, 0.2, 1))
        ]
        
        for text, analysis_type, color in analysis_options:
            btn = MDRaisedButton(
                text=text,
                size_hint_x=1,
                height=dp(40),
                md_bg_color=color,
                font_size="12sp"
            )
            buttons_layout.add_widget(btn)
        
        options_card.add_widget(buttons_layout)
        
        # Comprehensive button
        comprehensive_btn = MDRaisedButton(
            text="🏆 Run Full Analysis Suite",
            size_hint_y=None,
            height=dp(48),
            md_bg_color=(0.8, 0.2, 0.8, 1),
            font_size="14sp"
        )
        options_card.add_widget(comprehensive_btn)
        
        content.add_widget(options_card)
        print(f"[DEBUG] Added analysis options card")
        
        print(f"[DEBUG] Fixed-height analytics interface created successfully!")
        print(f"[DEBUG] Total content children: {len(content.children)}")
    
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
            height=dp(500),  # Larger for tablets
            adaptive_height=True
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
            adaptive_height=True
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
            height=dp(600),
            adaptive_height=True
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
            adaptive_height=True,
            padding=[self.TABLET_PADDING, self.TABLET_PADDING, self.TABLET_PADDING, self.TABLET_PADDING]
        )
        
        # Format and display results with better tablet formatting
        formatted_results = self._format_tablet_analysis_results(analysis_type, result)
        
        results_label = MDLabel(
            text=formatted_results,
            font_style="Body1",  # Larger font for tablets
            theme_text_color="Secondary",
            size_hint_y=None,
            adaptive_height=True,
            text_size=(None, None)
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