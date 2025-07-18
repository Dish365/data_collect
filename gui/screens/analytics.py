from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.slider import MDSlider
from kivy.core.window import Window

import threading
import json
from datetime import datetime

Builder.load_file('kv/analytics.kv')

class AnalyticsTab(MDBoxLayout, MDTabsBase):
    """Base class for analytics tab content"""
    pass

class AutoDetectionTab(AnalyticsTab):
    """Auto-detection and overview tab"""
    pass

class DescriptiveTab(AnalyticsTab):
    """Descriptive analytics tab"""
    pass

class InferentialTab(AnalyticsTab):
    """Inferential statistics tab"""
    pass

class QualitativeTab(AnalyticsTab):
    """Qualitative analytics tab"""
    pass

class AnalyticsScreen(Screen):
    # Properties
    current_project_id = StringProperty(None, allownone=True)
    current_project_name = StringProperty("")
    project_list = ListProperty([])
    project_map = {}
    
    # Analysis state
    is_loading = BooleanProperty(False)
    current_tab = StringProperty("auto_detection")
    analysis_results = ObjectProperty({})
    
    # UI references
    project_menu = None
    analytics_service = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analysis_results = {}
        Window.bind(on_resize=self.on_window_resize)

    def on_enter(self):
        """Initialize analytics screen when entered"""
        Clock.schedule_once(self._delayed_init, 0.1)

    def _delayed_init(self, dt):
        """Delayed initialization to ensure all widgets are ready"""
        # Set top bar title
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Analytics")
        
        self.setup_analytics_service()
        self.load_projects()
        self.setup_tabs()
        self.update_responsive_layout()
        self.update_quick_stats()

    def setup_analytics_service(self):
        """Initialize analytics service"""
        app = App.get_running_app()
        if not self.analytics_service:
            from services.analytics_service import AnalyticsService
            self.analytics_service = AnalyticsService(
                app.auth_service,
                app.db_service
            )

    def load_projects(self):
        """Load available projects for analysis"""
        try:
            app = App.get_running_app()
            conn = app.db_service.get_db_connection()
            
            if conn is None:
                toast("Database not initialized")
                return
                
            cursor = conn.cursor()
            user_data = app.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if user_id:
                cursor.execute("""
                    SELECT id, name, description, created_at,
                           (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count
                    FROM projects 
                    WHERE user_id = ? 
                    ORDER BY name
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT id, name, description, created_at,
                           (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count
                    FROM projects 
                    ORDER BY name
                """)
                
            projects = cursor.fetchall()
            
            if not projects:
                self.show_no_projects_state()
                return
                
            self.project_list = [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'description': p['description'] or '',
                    'response_count': p['response_count'] or 0,
                    'created_at': p['created_at']
                }
                for p in projects
            ]
            
            self.project_map = {p['name']: p['id'] for p in projects}
            
            # Update project selector
            if hasattr(self.ids, 'project_selector'):
                self.ids.project_selector.text = "Select Project for Analysis"
                
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast("Error loading projects")
        finally:
            if conn:
                conn.close()

    def show_no_projects_state(self):
        """Show message when no projects are available"""
        toast("No projects found. Create a project first to analyze data.")

    def open_project_menu(self):
        """Open project selection dropdown menu"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        if not self.project_list:
            toast("No projects available")
            return
            
        menu_items = []
        for project in self.project_list:
            menu_items.append({
                "text": f"{project['name']} ({project['response_count']} responses)",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=project: self.select_project(x)
            })
            
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_selector,
            items=menu_items,
            width_mult=4
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project for analysis"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        self.current_project_id = project['id']
        self.current_project_name = project['name']
        
        # Update project selector text
        if hasattr(self.ids, 'project_selector'):
            self.ids.project_selector.text = project['name']
        
        # Update quick stats and load data characteristics
        self.update_quick_stats()
        self.load_project_data_characteristics()
        
        toast(f"Selected project: {project['name']}")

    def setup_tabs(self):
        """Setup the analytics tabs"""
        if not hasattr(self.ids, 'analytics_tabs'):
            return
            
        tabs = self.ids.analytics_tabs
        tabs.bind(on_tab_switch=self.on_tab_switch)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Handle tab switching"""
        tab_map = {
            "Auto-Detection": "auto_detection",
            "Descriptive": "descriptive", 
            "Inferential": "inferential",
            "Qualitative": "qualitative"
        }
        
        self.current_tab = tab_map.get(tab_text, "auto_detection")
        self.load_tab_content()

    def load_tab_content(self):
        """Load content for the current tab"""
        if not self.current_project_id:
            return
            
        if self.current_tab == "auto_detection":
            self.load_auto_detection()
        elif self.current_tab == "descriptive":
            self.load_descriptive()
        elif self.current_tab == "inferential":
            self.load_inferential()
        elif self.current_tab == "qualitative":
            self.load_qualitative()

    def update_quick_stats(self):
        """Update the quick statistics cards"""
        if not hasattr(self.ids, 'stats_container'):
            return
            
        try:
            stats_container = self.ids.stats_container
            stats_container.clear_widgets()
            
            if not self.current_project_id:
                return
                
            stats = self.get_project_stats()
            
            stat_items = [
                ("Total Responses", stats.get('total_responses', 0), "database", "Total survey responses"),
                ("Questions", stats.get('total_questions', 0), "help-circle", "Questions in project"),
                ("Completion Rate", f"{stats.get('completion_rate', 0)}%", "check-circle", "Response completion rate"),
                ("Last Updated", stats.get('last_updated', 'Never'), "clock", "Most recent activity"),
            ]
            
            from widgets.analytics_stat_card import AnalyticsStatCard
            for label, value, icon, note in stat_items:
                try:
                    card = AnalyticsStatCard(
                        title=label, 
                        value=str(value), 
                        icon=icon, 
                        note=note
                    )
                    stats_container.add_widget(card)
                except Exception as card_error:
                    print(f"Error creating stat card for {label}: {card_error}")
                    
        except Exception as e:
            print(f"Error updating quick stats: {e}")

    def get_project_stats(self):
        """Get statistics for the current project"""
        if not self.current_project_id:
            return {}
            
        try:
            # Use analytics service for project stats
            stats = self.analytics_service.get_project_stats(self.current_project_id)
            
            if 'error' in stats:
                print(f"Error getting project stats: {stats['error']}")
                return {}
            
            # Calculate completion rate
            completion_rate = 0
            total_responses = stats.get('total_responses', 0)
            total_questions = stats.get('total_questions', 0)
            unique_respondents = stats.get('unique_respondents', 0)
            
            if total_questions > 0 and unique_respondents > 0:
                expected_total = total_questions * unique_respondents
                completion_rate = min(100, (total_responses / expected_total) * 100) if expected_total > 0 else 0
                
            return {
                'total_responses': total_responses,
                'total_questions': total_questions,
                'completion_rate': round(completion_rate, 1),
                'unique_respondents': unique_respondents,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
        except Exception as e:
            print(f"Error getting project stats: {e}")
            return {}

    def load_project_data_characteristics(self):
        """Load data characteristics for auto-detection"""
        if not self.current_project_id:
            return
            
        threading.Thread(
            target=self._load_data_characteristics_thread,
            daemon=True
        ).start()

    def _load_data_characteristics_thread(self):
        """Background thread to load data characteristics"""
        try:
            if self.analytics_service:
                characteristics = self.analytics_service.get_data_characteristics(
                    self.current_project_id
                )
                Clock.schedule_once(
                    lambda dt: self._update_data_characteristics(characteristics), 0
                )
        except Exception as e:
            print(f"Error loading data characteristics: {e}")

    def _update_data_characteristics(self, characteristics):
        """Update UI with data characteristics"""
        self.analysis_results['data_characteristics'] = characteristics

    # Analysis Methods
    
    def load_auto_detection(self):
        """Load auto-detection recommendations"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        self.set_loading(True)
        threading.Thread(target=self._load_auto_detection_thread, daemon=True).start()

    def _load_auto_detection_thread(self):
        """Background thread for auto-detection"""
        try:
            if self.analytics_service:
                # Get analysis recommendations
                recommendations = self.analytics_service.get_analysis_recommendations(
                    self.current_project_id
                )
                
                # Run auto analysis to get actual results
                analysis_results = self.analytics_service.run_analysis(
                    self.current_project_id, "auto"
                )
                
                # Combine results
                combined_results = {
                    'recommendations': recommendations,
                    'analysis_results': analysis_results
                }
                
                Clock.schedule_once(
                    lambda dt: self._display_auto_detection(combined_results), 0
                )
        except Exception as e:
            print(f"Error in auto-detection: {e}")
            Clock.schedule_once(lambda dt: self.show_error("Auto-detection failed"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_auto_detection(self, results):
        """Display auto-detection recommendations"""
        if not hasattr(self.ids, 'auto_detection_content'):
            return
            
        content = self.ids.auto_detection_content
        content.clear_widgets()
        
        if not results:
            content.add_widget(self.create_empty_state_widget(
                "No analysis recommendations available.\nPlease ensure the FastAPI backend is running."
            ))
            return
        
        # Check for backend connection errors
        recommendations = results.get('recommendations', {})
        analysis_results = results.get('analysis_results', {})
        
        if 'error' in recommendations and 'Cannot connect to analytics backend' in recommendations['error']:
            content.add_widget(self.create_backend_error_widget())
            return
        
        if 'error' in analysis_results and 'Cannot connect to analytics backend' in analysis_results['error']:
            content.add_widget(self.create_backend_error_widget())
            return
        
        # Display recommendations
        if recommendations and 'error' not in recommendations:
            self.display_recommendations(content, recommendations)
        
        # Display analysis results
        if analysis_results and 'analyses' in analysis_results:
            self.display_analysis_results(content, analysis_results['analyses'])
        
        # If no valid results, show empty state
        if not recommendations and not analysis_results:
            content.add_widget(self.create_empty_state_widget(
                "No analysis recommendations available at this time."
            ))

    def display_recommendations(self, content, recommendations):
        """Display recommendations in content area"""
        for category, recs in recommendations.items():
            if recs and isinstance(recs, list):
                # Category header
                header = MDLabel(
                    text=category.replace('_', ' ').title(),
                    font_style="H6",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(48)
                )
                content.add_widget(header)
                
                # Show top 3 recommendations
                for rec in recs[:3]:
                    rec_card = self.create_recommendation_card(rec)
                    content.add_widget(rec_card)

    def display_analysis_results(self, content, analyses):
        """Display analysis results in content area"""
        # Results header
        results_header = MDLabel(
            text="Analysis Results",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(results_header)
        
        # Display each analysis result
        for analysis_type, result in analyses.items():
            if result and 'error' not in result:
                analysis_card = self.create_analysis_results_card(analysis_type, result)
                content.add_widget(analysis_card)

    def create_recommendation_card(self, recommendation):
        """Create a recommendation card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(120),
            elevation=2
        )
        
        # Title
        title = MDLabel(
            text=recommendation.get('method', 'Unknown Method'),
            font_style="Subtitle1",
            theme_text_color="Primary"
        )
        card.add_widget(title)
        
        # Description
        desc = MDLabel(
            text=recommendation.get('rationale', 'No description available'),
            font_style="Body2",
            theme_text_color="Secondary"
        )
        card.add_widget(desc)
        
        # Action button
        action_btn = MDRaisedButton(
            text="Run Analysis",
            size_hint=(None, None),
            height=dp(36),
            width=dp(120),
            on_release=lambda x: self.run_recommended_analysis(recommendation)
        )
        card.add_widget(action_btn)
        
        return card

    def create_analysis_results_card(self, analysis_type, result):
        """Create a card to display analysis results"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(150),
            elevation=2
        )
        
        # Analysis type header
        header = MDLabel(
            text=analysis_type.replace('_', ' ').title(),
            font_style="H6",
            theme_text_color="Primary"
        )
        card.add_widget(header)
        
        # Result summary
        summary_text = self.format_analysis_summary(result)
        summary_label = MDLabel(
            text=summary_text,
            font_style="Body2",
            theme_text_color="Secondary"
        )
        card.add_widget(summary_label)
        
        return card

    def format_analysis_summary(self, result):
        """Format analysis result for display"""
        if isinstance(result, dict):
            if 'summary' in result:
                summary = result['summary']
                return f"Variables analyzed: {summary.get('variables_analyzed', 'N/A')}"
            elif 'basic_statistics' in result:
                stats = result['basic_statistics']
                return f"Statistics calculated for {len(stats)} variables"
            elif 'correlation_matrix' in result:
                corr = result['correlation_matrix']
                return f"Correlation matrix: {len(corr)} x {len(corr)}"
            else:
                return "Analysis completed successfully"
        return "Analysis completed"

    def create_empty_state_widget(self, message):
        """Create an empty state widget"""
        return MDLabel(
            text=message,
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1"
        )

    def run_recommended_analysis(self, recommendation):
        """Run a recommended analysis"""
        method = recommendation.get('method', '')
        category = recommendation.get('category', 'descriptive')
        
        if category == 'descriptive':
            self.load_descriptive()
        elif category == 'qualitative':
            self.load_qualitative()
        else:
            toast(f"Running {method} analysis...")

    def load_descriptive(self):
        """Load descriptive analytics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        self.set_loading(True)
        threading.Thread(target=self._load_descriptive_thread, daemon=True).start()

    def _load_descriptive_thread(self):
        """Background thread for descriptive analytics"""
        try:
            if self.analytics_service:
                results = self.analytics_service.run_analysis(
                    self.current_project_id, "descriptive"
                )
                Clock.schedule_once(
                    lambda dt: self._display_descriptive_results(results), 0
                )
        except Exception as e:
            print(f"Error in descriptive analysis: {e}")
            Clock.schedule_once(lambda dt: self.show_error("Descriptive analysis failed"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_descriptive_results(self, results):
        """Display descriptive analysis results"""
        if not hasattr(self.ids, 'descriptive_content'):
            return
            
        content = self.ids.descriptive_content
        content.clear_widgets()
        
        if not results:
            content.add_widget(self.create_empty_state_widget(
                "No descriptive analysis results available.\nPlease ensure the FastAPI backend is running."
            ))
            return
            
        if 'error' in results:
            error_message = results['error']
            if 'Cannot connect to analytics backend' in error_message:
                content.add_widget(self.create_backend_error_widget())
            else:
                content.add_widget(self.create_empty_state_widget(
                    f"Analysis Error: {error_message}"
                ))
            return
            
        # Display results
        stats_card = self.create_results_display_card("Descriptive Statistics", results)
        content.add_widget(stats_card)
    
    def create_backend_error_widget(self):
        """Create a widget for backend connection errors"""
        error_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(200),
            elevation=2,
            md_bg_color=(1, 0.9, 0.9, 1)  # Light red background
        )
        
        # Error icon and title
        title_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32)
        )
        
        error_icon = MDIconButton(
            icon="alert-circle",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(32)
        )
        
        error_title = MDLabel(
            text="Analytics Backend Not Available",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1)
        )
        
        title_layout.add_widget(error_icon)
        title_layout.add_widget(error_title)
        error_card.add_widget(title_layout)
        
        # Error message
        error_message = MDLabel(
            text="The analytics backend is not responding. Please ensure:\n" +
                 "1. The FastAPI server is running on port 8001\n" +
                 "2. Run: python backend/fastapi/start_analytics_backend.py\n" +
                 "3. Check the backend logs for errors",
            font_style="Body2",
            theme_text_color="Custom",
            text_color=(0.6, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(100)
        )
        error_card.add_widget(error_message)
        
        # Retry button
        retry_button = MDRaisedButton(
            text="Retry Connection",
            size_hint=(None, None),
            height=dp(36),
            width=dp(160),
            on_release=lambda x: self.load_tab_content()
        )
        error_card.add_widget(retry_button)
        
        return error_card

    def create_results_display_card(self, title, results):
        """Create a card to display analysis results"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(300),
            elevation=2
        )
        
        # Title
        title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Primary"
        )
        card.add_widget(title_label)
        
        # Results content - formatted display
        if isinstance(results, dict):
            if 'analyses' in results:
                # Show analysis results
                analyses = results['analyses']
                for analysis_type, analysis_data in analyses.items():
                    if analysis_data and 'error' not in analysis_data:
                        # Analysis type subheader
                        subheader = MDLabel(
                            text=f"• {analysis_type.replace('_', ' ').title()}",
                            font_style="Subtitle1",
                            theme_text_color="Primary",
                            size_hint_y=None,
                            height=dp(24)
                        )
                        card.add_widget(subheader)
                        
                        # Analysis details
                        details_text = self.format_analysis_details(analysis_data)
                        details_label = MDLabel(
                            text=details_text,
                            font_style="Body2",
                            theme_text_color="Secondary",
                            size_hint_y=None,
                            height=dp(60)
                        )
                        card.add_widget(details_label)
            else:
                # Single analysis result
                details_text = self.format_analysis_details(results)
                details_label = MDLabel(
                    text=details_text,
                    font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(200)
                )
                card.add_widget(details_label)
        else:
            # Fallback to string representation
            results_text = str(results)[:300] + "..." if len(str(results)) > 300 else str(results)
            results_label = MDLabel(
                text=results_text,
                font_style="Body2",
                theme_text_color="Secondary"
            )
            card.add_widget(results_label)
        
        return card
    
    def format_analysis_details(self, analysis_data):
        """Format analysis data for display"""
        if not isinstance(analysis_data, dict):
            return str(analysis_data)
        
        formatted_lines = []
        
        # Handle different analysis result formats
        if 'basic_statistics' in analysis_data:
            stats = analysis_data['basic_statistics']
            if 'numeric' in stats:
                formatted_lines.append(f"Numeric variables: {len(stats['numeric'])}")
            if 'categorical' in stats:
                formatted_lines.append(f"Categorical variables: {len(stats['categorical'])}")
        
        if 'summary' in analysis_data:
            summary = analysis_data['summary']
            if 'total_responses' in summary:
                formatted_lines.append(f"Total responses: {summary['total_responses']}")
            if 'total_variables' in summary:
                formatted_lines.append(f"Total variables: {summary['total_variables']}")
        
        if 'data_characteristics' in analysis_data:
            char = analysis_data['data_characteristics']
            if 'sample_size' in char:
                formatted_lines.append(f"Sample size: {char['sample_size']}")
            if 'completeness_score' in char:
                formatted_lines.append(f"Data completeness: {char['completeness_score']:.1f}%")
        
        if 'error' in analysis_data:
            formatted_lines.append(f"Error: {analysis_data['error']}")
        
        if not formatted_lines:
            # Generic formatting for unknown structures
            for key, value in analysis_data.items():
                if isinstance(value, (str, int, float)):
                    formatted_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_lines[:5]) if formatted_lines else "Analysis completed successfully"

    def load_inferential(self):
        """Load inferential statistics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        toast("Inferential statistics coming soon!")

    def load_qualitative(self):
        """Load qualitative analytics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        toast("Qualitative analytics coming soon!")

    # Utility Methods
    
    def show_select_project_message(self):
        """Show message to select a project first"""
        toast("Please select a project first")

    def set_loading(self, loading):
        """Set loading state"""
        self.is_loading = loading
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = loading

    def show_error(self, message):
        """Show error message"""
        toast(f"Error: {message}")

    def refresh_analysis(self):
        """Refresh current analysis"""
        if self.current_project_id:
            self.load_tab_content()
        else:
            toast("Select a project first")

    def export_results(self):
        """Export analysis results"""
        if not self.analysis_results:
            toast("No results to export")
            return
            
        toast("Export functionality coming soon!")

    def show_analysis_config(self):
        """Show analysis configuration dialog"""
        toast("Analysis configuration coming soon")
        
    def on_window_resize(self, window, width, height):
        """Handle window resize"""
        self.update_responsive_layout()

    def update_responsive_layout(self):
        """Update responsive layout based on screen size"""
        try:
            window_width = Window.width
            
            # Calculate optimal columns for stats cards
            if window_width < 700:
                stats_cols = 1
            elif window_width < 1200:
                stats_cols = 2
            else:
                stats_cols = 4
                
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.cols = stats_cols
                
        except Exception as e:
            print(f"Error in responsive layout: {e}")
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.cols = 1 