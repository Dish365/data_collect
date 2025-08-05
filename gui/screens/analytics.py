from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from utils.cross_platform_toast import toast
from kivy.core.window import Window
from widgets.top_bar import TopBar
from widgets.two_line_menu_item import TwoLineMenuItem
from kivymd.uix.menu import MDDropdownMenu

import threading
from datetime import datetime
from typing import Dict, List

#:kivy 2.0

# KV file loaded by main app after theme initialization

class AnalyticsScreen(Screen):
    """Analytics Screen - Navigation hub for analytics features
    
    This screen serves as the central hub for all analytics capabilities:
    - Descriptive Analytics: 22 functions for basic statistics, distributions, and patterns
    - Qualitative Analytics: 36 functions for text analysis, sentiment, and themes
    - Inferential Analytics: 89 functions for hypothesis testing, regression, and statistical inference
    - Auto Detection: Automated analysis recommendations and pattern detection
    - Data Exploration: Interactive data browsing and visualization
    
    Total: 147+ individual analytics methods available across all modules
    """
    
    # Properties
    current_project_id = StringProperty(None, allownone=True)
    current_project_name = StringProperty("")
    project_list = ListProperty([])
    project_map = {}
    
    # UI state
    is_project_overview_collapsed = BooleanProperty(False)
    
    # Analytics capabilities metadata
    analytics_categories = {
        'descriptive': {
            'name': 'Descriptive Analytics',
            'description': 'Statistical summaries, distributions, and data patterns',
            'function_count': 22,
            'categories': ['Basic Statistics', 'Categorical Analysis', 'Distribution Analysis', 'Geospatial Analysis', 'Temporal Analysis'],
            'key_features': ['Central tendency measures', 'Correlation analysis', 'Distribution fitting', 'Spatial patterns', 'Time series patterns']
        },
        'qualitative': {
            'name': 'Qualitative Analytics',  
            'description': 'Text analysis, sentiment detection, and thematic exploration',
            'function_count': 36,
            'categories': ['Content Analysis', 'Sentiment Analysis', 'Thematic Analysis', 'Survey Analysis', 'Text Processing'],
            'key_features': ['Sentiment scoring', 'Theme identification', 'Content categorization', 'Response quality assessment', 'Linguistic analysis']
        },
        'inferential': {
            'name': 'Inferential Analytics',
            'description': 'Statistical testing, confidence intervals, and predictive modeling',
            'function_count': 89,
            'categories': ['Hypothesis Testing', 'Regression Analysis', 'Bayesian Inference', 'Bootstrap Methods', 'Power Analysis'],
            'key_features': ['Statistical significance testing', 'Effect size calculations', 'Confidence intervals', 'Model diagnostics', 'Sample size planning']
        },
        'auto_detection': {
            'name': 'Auto Detection',
            'description': 'Automated analysis recommendations and pattern recognition',
            'function_count': 'AI-Powered',
            'categories': ['Pattern Detection', 'Analysis Recommendations', 'Data Quality Assessment', 'Anomaly Detection'],
            'key_features': ['Smart analysis suggestions', 'Data quality scoring', 'Automated insights', 'Pattern recognition', 'Outlier detection']
        },
        'data_exploration': {
            'name': 'Data Exploration',
            'description': 'Interactive data browsing, filtering, and visualization',
            'function_count': 'Interactive',
            'categories': ['Data Browsing', 'Filtering', 'Visualization', 'Export Tools'],
            'key_features': ['Raw data inspection', 'Advanced filtering', 'Interactive charts', 'Data export options', 'Response tracking']
        }
    }
    
    # UI references
    project_menu = None
    analytics_service = None
    
    # UI constants
    CARD_HEIGHT = dp(200)
    PADDING = dp(24)
    SPACING = dp(20)
    BUTTON_HEIGHT = dp(48)
    ICON_SIZE = dp(32)
    FONT_SIZE = "16sp"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)

    def _detect_tablet(self):
        """Detect if we're running on a tablet-sized device"""
        width = Window.width
        return 768 <= width <= 1366

    def _get_project_selector(self):
        """Helper method to get the project selector widget"""
        if hasattr(self.ids, 'project_selector') and self.ids.project_selector:
            return self.ids.project_selector
        return None
        
    def _get_project_name_label(self):
        """Helper method to get the project name label widget"""
        project_selector = self._get_project_selector()
        if project_selector and hasattr(project_selector.ids, 'project_name_label'):
            return project_selector.ids.project_name_label
        return None



    def on_enter(self):
        """Initialize analytics screen when entered"""
        Clock.schedule_once(self._delayed_init, 0.1)

    def _delayed_init(self, dt):
        """Delayed initialization"""
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Analytics Hub")
            self.ids.top_bar.set_current_screen('analytics')
        
        self.setup_analytics_service()
        self.load_projects()
        self.update_responsive_layout()
        self.update_quick_stats()
        self.update_project_overview_collapse_state()
        
        # Ensure project selector is initialized
        Clock.schedule_once(self._initialize_project_selector, 0.2)

    def setup_analytics_service(self):
        """Initialize basic analytics service"""
        app = App.get_running_app()
        if not self.analytics_service:
            from services.analytics_service import AnalyticsService
            self.analytics_service = AnalyticsService(
                app.auth_service,
                app.db_service
            )

    def load_projects(self):
        """Load available projects"""
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
                           (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count,
                           (SELECT COUNT(DISTINCT respondent_id) FROM responses WHERE project_id = projects.id) as respondent_count
                    FROM projects 
                    WHERE user_id = ? 
                    ORDER BY name
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT id, name, description, created_at,
                           (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count,
                           (SELECT COUNT(DISTINCT respondent_id) FROM responses WHERE project_id = projects.id) as respondent_count
                    FROM projects 
                    ORDER BY name
                """)
                
            projects = cursor.fetchall()
            
            if not projects:
                toast("No projects available. Create a project first.")
                return
                
            self.project_list = [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'description': p['description'] or '',
                    'response_count': p['response_count'] or 0,
                    'respondent_count': p['respondent_count'] or 0,
                    'created_at': p['created_at']
                }
                for p in projects
            ]
            
            self.project_map = {p['name']: p['id'] for p in projects}
            
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast("Error loading projects")
        finally:
            if conn:
                conn.close()

    def _initialize_project_selector(self, dt):
        """Initialize project selector with better error handling"""
        # Debug: Print all available IDs
        print(f"Available IDs in analytics screen: {list(self.ids.keys())}")
        
        project_selector = self._get_project_selector()
        project_name_label = self._get_project_name_label()
        
        if project_selector:
            if not self.current_project_id:
                # Update the project name label
                if project_name_label:
                    project_name_label.text = "No project selected - Click to choose"
            print("Project selector initialized successfully")
        else:
            print("Warning: project_selector still not found, will retry on user interaction")
            # Try one more time with a longer delay
            Clock.schedule_once(self._initialize_project_selector, 1.0)

    def open_project_menu(self, retry_count=0):
        """Open project selection dropdown menu"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        if not self.project_list:
            toast("No projects available")
            return
        
        project_selector = self._get_project_selector()
        
        # Check if project_selector exists, retry with delay if not available
        if not project_selector:
            if retry_count < 3:  # Limit retries to prevent infinite loop
                print(f"Warning: project_selector not found in analytics screen, retrying... (attempt {retry_count + 1})")
                Clock.schedule_once(lambda dt: self.open_project_menu(retry_count + 1), 0.5)
            else:
                print("Error: project_selector not found after 3 attempts, showing toast instead")
                toast("Project selector not available")
            return
            
        menu_items = []
        for project in self.project_list:
            # Create separate headline and supporting text
            headline_text = project['name']
            supporting_text = f"{project['response_count']} responses • {project['respondent_count']} respondents"
            
            menu_items.append({
                "headline": headline_text,
                "supporting": supporting_text,
                "viewclass": "TwoLineMenuItem",
                "height": dp(72),
                "on_release": lambda x=project: self.select_project(x)
            })
            
        self.project_menu = MDDropdownMenu(
            caller=project_selector,
            items=menu_items,
            width=dp(240),
            max_height=dp(400)
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        self.current_project_id = project['id']
        self.current_project_name = project['name']
        
        # Update the project name label in the new ProjectSelectorCard
        project_name_label = self._get_project_name_label()
        if project_name_label:
            label_text = f"{project['name']}"
            if project['response_count'] > 0:
                label_text += f" ({project['response_count']} responses)"
            project_name_label.text = label_text
        
        # Update the project overview header text
        if hasattr(self.ids, 'project_overview_header') and hasattr(self.ids.project_overview_header.ids, 'project_overview_label'):
            self.ids.project_overview_header.ids.project_overview_label.text = f"{project['name']} Overview"
        
        # Update the stats immediately
        print(f"Project selected: {project['name']} (ID: {project['id']})")
        Clock.schedule_once(lambda dt: self.update_quick_stats(), 0.1)
        
        # Refresh project overview
        Clock.schedule_once(lambda dt: self.refresh_project_overview(), 0.2)
        
        toast(f"Selected: {project['name']}")

    def refresh_project_overview(self):
        """Refresh the project overview card"""
        try:
            # Update the project overview header text
            if hasattr(self.ids, 'project_overview_header') and hasattr(self.ids.project_overview_header.ids, 'project_overview_label'):
                if self.current_project_name:
                    self.ids.project_overview_header.ids.project_overview_label.text = f"{self.current_project_name} Overview"
                else:
                    self.ids.project_overview_header.ids.project_overview_label.text = "Project Overview"
            
            # Update the stats
            self.update_quick_stats()
            
            # Ensure the project overview is expanded
            if self.is_project_overview_collapsed:
                self.toggle_project_overview()
                
        except Exception as e:
            print(f"Error refreshing project overview: {e}")

    # Navigation methods
    def _navigate_to_screen(self, screen_name, display_name, pass_project_data=True):
        """Common navigation method with project data passing"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
            
        app = App.get_running_app()
        
        # Pass current project data to the target screen if supported
        if pass_project_data and hasattr(app.root, 'get_screen'):
            try:
                target_screen = app.root.get_screen(screen_name)
                if hasattr(target_screen, 'current_project_id'):
                    target_screen.current_project_id = self.current_project_id
                if hasattr(target_screen, 'current_project_name'):
                    target_screen.current_project_name = self.current_project_name
                if hasattr(target_screen, 'analytics_service'):
                    target_screen.analytics_service = self.analytics_service
            except Exception as e:
                print(f"Could not pass project data to {screen_name}: {e}")
        
        app.root.current = screen_name
        toast(f"Opening {display_name}...")

    def navigate_to_data_exploration(self):
        """Navigate to data exploration screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        app = App.get_running_app()
        
        # Pass project data to data exploration screen
        try:
            data_exploration_screen = app.root.get_screen('data_exploration')
            if hasattr(data_exploration_screen, 'set_project_from_analytics_hub'):
                data_exploration_screen.set_project_from_analytics_hub(
                    self.current_project_id, 
                    self.current_project_name
                )
        except Exception as e:
            print(f"Could not pass project data to data exploration: {e}")
        
        self._navigate_to_screen('data_exploration', 'Data Exploration', pass_project_data=True)

    def navigate_to_qualitative_analytics(self):
        """Navigate to qualitative analytics screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_to_screen('qualitative_analytics', 'Qualitative Analytics', pass_project_data=True)

    def navigate_to_descriptive_analytics(self):
        """Navigate to descriptive analytics screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_to_screen('descriptive_analytics', 'Descriptive Analytics', pass_project_data=True)

    def navigate_to_inferential_analytics(self):
        """Navigate to inferential analytics screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_to_screen('inferential_analytics', 'Inferential Analytics', pass_project_data=True)

    def navigate_to_auto_detection(self):
        """Navigate to auto detection screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_to_screen('auto_detection', 'Auto Detection', pass_project_data=True)
        
    def get_available_analytics_summary(self):
        """Get a summary of all available analytics capabilities"""
        total_functions = sum(
            cat['function_count'] for cat in self.analytics_categories.values() 
            if isinstance(cat['function_count'], int)
        )
        
        summary = f"Analytics Hub - {total_functions}+ Statistical Functions Available\n\n"
        
        for key, category in self.analytics_categories.items():
            summary += f"{category['name']}: "
            if isinstance(category['function_count'], int):
                summary += f"{category['function_count']} functions\n"
            else:
                summary += f"{category['function_count']}\n"
            summary += f"  {category['description']}\n\n"
            
        return summary
        
    def show_analytics_overview(self):
        """Show comprehensive analytics overview"""
        overview = self.get_available_analytics_summary()
        # Show detailed overview
        overview_text = "Analytics Hub Overview:\n\n"
        overview_text += "• Descriptive Analytics: 22 functions for statistical summaries\n"
        overview_text += "• Qualitative Analytics: 36 functions for text & sentiment analysis\n" 
        overview_text += "• Inferential Analytics: 89 functions for hypothesis testing\n"
        overview_text += "• Data Exploration: Interactive data browsing & filtering\n"
        overview_text += "• Auto Detection: AI-powered analysis recommendations\n\n"
        overview_text += "Select a project above to unlock all analytics capabilities!"
        toast(overview_text)
        
    def get_analytics_capabilities_by_category(self):
        """Get detailed breakdown of analytics capabilities"""
        capabilities = {}
        
        # Extract from analytics markdown documentation
        capabilities['descriptive'] = {
            'basic_statistics': ['calculate_basic_stats', 'calculate_percentiles', 'calculate_grouped_stats', 'calculate_weighted_stats', 'calculate_correlation_matrix', 'calculate_covariance_matrix'],
            'categorical_analysis': ['analyze_categorical', 'calculate_chi_square', 'calculate_cramers_v', 'analyze_cross_tabulation', 'calculate_diversity_metrics', 'analyze_categorical_associations'],
            'distribution_analysis': ['analyze_distribution', 'test_normality', 'calculate_skewness_kurtosis', 'fit_distribution'],
            'geospatial_analysis': ['analyze_spatial_distribution', 'calculate_spatial_autocorrelation', 'create_location_clusters'],
            'temporal_analysis': ['analyze_temporal_patterns', 'calculate_time_series_stats', 'detect_seasonality']
        }
        
        capabilities['qualitative'] = {
            'content_analysis': ['analyze_content_structure', 'analyze_content_categories', 'analyze_linguistic_features', 'analyze_content_patterns', 'analyze_content_by_metadata', 'analyze_content_comprehensively'],
            'sentiment_analysis': ['analyze_sentiment', 'analyze_sentiment_batch', 'analyze_emotions', 'analyze_sentiment_trends', 'analyze_sentiment_by_question', 'detect_sentiment_patterns', 'generate_sentiment_summary'],
            'text_analysis': ['preprocess_text', 'analyze_text_frequency', 'analyze_text_similarity', 'extract_key_phrases', 'analyze_text_patterns'],
            'thematic_analysis': ['extract_key_concepts', 'identify_themes_clustering', 'identify_themes_lda', 'analyze_theme_evolution', 'extract_quotes_by_theme', 'analyze_theme_relationships', 'generate_theme_report', 'analyze_themes'],
            'survey_analysis': ['analyze_response_quality', 'analyze_survey_by_questions', 'compare_questions', 'analyze_respondent_patterns', 'generate_survey_report', 'analyze_survey_data']
        }
        
        capabilities['inferential'] = {
            'hypothesis_testing': ['perform_t_test', 'perform_paired_t_test', 'perform_welch_t_test', 'perform_anova', 'perform_two_way_anova', 'perform_repeated_measures_anova', 'perform_chi_square_test', 'perform_fisher_exact_test', 'perform_mcnemar_test', 'perform_correlation_test', 'perform_partial_correlation', 'hypothesis_test_summary'],
            'regression_analysis': ['perform_linear_regression', 'perform_multiple_regression', 'perform_logistic_regression', 'perform_poisson_regression', 'calculate_regression_diagnostics', 'calculate_vif', 'perform_ridge_regression', 'perform_lasso_regression', 'perform_robust_regression'],
            'bayesian_inference': ['bayesian_t_test', 'bayesian_proportion_test', 'calculate_bayes_factor', 'calculate_posterior_distribution', 'calculate_credible_interval', 'bayesian_ab_test'],
            'bootstrap_methods': ['bootstrap_mean', 'bootstrap_median', 'bootstrap_correlation', 'bootstrap_regression', 'bootstrap_std', 'bootstrap_quantile', 'bootstrap_difference_means', 'bootstrap_ratio_means', 'permutation_test', 'jackknife_estimate', 'bootstrap_hypothesis_test'],
            'power_analysis': ['calculate_sample_size_t_test', 'calculate_sample_size_anova', 'calculate_sample_size_proportion', 'calculate_sample_size_correlation', 'calculate_power_t_test', 'calculate_power_anova', 'calculate_effect_size_needed', 'post_hoc_power_analysis']
        }
        
        return capabilities
        
    def get_function_documentation_summary(self):
        """Get summary of key function categories and their purposes"""
        return {
            'descriptive_highlights': [
                'Basic Statistics: Mean, median, mode, standard deviation, variance, correlation matrices',
                'Categorical Analysis: Chi-square tests, Cramér\'s V, cross-tabulation, diversity metrics', 
                'Distribution Analysis: Normality testing, distribution fitting, skewness/kurtosis',
                'Geospatial Analysis: Spatial clustering, hotspot analysis, autocorrelation',
                'Temporal Analysis: Time series patterns, seasonality detection, trend analysis'
            ],
            'qualitative_highlights': [
                'Content Analysis: Text structure, linguistic features, content categorization',
                'Sentiment Analysis: Polarity scoring, emotion detection, sentiment trends',
                'Text Processing: Frequency analysis, similarity, key phrase extraction',
                'Thematic Analysis: Topic modeling, theme identification, concept extraction',
                'Survey Analysis: Response quality, question comparison, pattern analysis'
            ],
            'inferential_highlights': [
                'Hypothesis Testing: t-tests, ANOVA, chi-square, correlation significance',
                'Regression Analysis: Linear, logistic, Poisson, robust regression with diagnostics',
                'Bayesian Inference: Bayesian t-tests, credible intervals, Bayes factors',
                'Bootstrap Methods: Non-parametric confidence intervals, permutation tests',
                'Power Analysis: Sample size calculations, effect size estimation'
            ]
        }

    def toggle_project_overview(self):
        """Toggle the project overview collapsible state"""
        self.is_project_overview_collapsed = not self.is_project_overview_collapsed
        self.update_project_overview_collapse_state()
    
    def update_project_overview_collapse_state(self):
        """Update the visual state of the collapsible project overview"""
        try:
            # Try to access content through different paths
            content = None
            
            # Try direct access
            if hasattr(self.ids, 'project_overview_content'):
                content = self.ids.project_overview_content
                print("Found project_overview_content directly")
            # Try through project_overview_card
            elif hasattr(self.ids, 'project_overview_card') and hasattr(self.ids.project_overview_card.ids, 'project_overview_content'):
                content = self.ids.project_overview_card.ids.project_overview_content
                print("Found project_overview_content through project_overview_card")
            else:
                print("Warning: project_overview_content not found")
                print(f"Available IDs in project_overview_card: {list(self.ids.project_overview_card.ids.keys()) if hasattr(self.ids, 'project_overview_card') else 'No project_overview_card'}")
                return
            
            # Access toggle button through the header
            toggle_button = None
            if hasattr(self.ids, 'project_overview_header') and hasattr(self.ids.project_overview_header.ids, 'stats_toggle_button'):
                toggle_button = self.ids.project_overview_header.ids.stats_toggle_button
            elif hasattr(self.ids, 'project_overview_card') and hasattr(self.ids.project_overview_card.ids, 'project_overview_header') and hasattr(self.ids.project_overview_card.ids.project_overview_header.ids, 'stats_toggle_button'):
                toggle_button = self.ids.project_overview_card.ids.project_overview_header.ids.stats_toggle_button
            else:
                print("Warning: stats_toggle_button not found")
                return
                
            project_overview_card = self.ids.project_overview_card
            
            if self.is_project_overview_collapsed:
                content.height = 0
                content.opacity = 0
                toggle_button.icon = "chevron-right"
                project_overview_card.height = dp(88)
                print("Project overview collapsed")
            else:
                content.height = dp(176)
                content.opacity = 1
                toggle_button.icon = "chevron-down"
                project_overview_card.height = dp(264)
                print("Project overview expanded")
                
        except Exception as e:
            print(f"Error updating project overview collapse state: {e}")

    def update_quick_stats(self):
        """Update quick statistics using existing StatCard widget"""
        try:
            # Try to access stats_container through different paths
            stats_container = None
            
            # Try direct access
            if hasattr(self.ids, 'stats_container'):
                stats_container = self.ids.stats_container
                print(f"Found stats_container directly, clearing widgets...")
            # Try through project_overview_content
            elif hasattr(self.ids, 'project_overview_content') and hasattr(self.ids.project_overview_content.ids, 'stats_container'):
                stats_container = self.ids.project_overview_content.ids.stats_container
                print(f"Found stats_container through project_overview_content, clearing widgets...")
            # Try through project_overview_card
            elif hasattr(self.ids, 'project_overview_card') and hasattr(self.ids.project_overview_card.ids, 'project_overview_content') and hasattr(self.ids.project_overview_card.ids.project_overview_content.ids, 'stats_container'):
                stats_container = self.ids.project_overview_card.ids.project_overview_content.ids.stats_container
                print(f"Found stats_container through project_overview_card, clearing widgets...")
            else:
                print("Warning: stats_container not found")
                print(f"Available IDs in analytics screen: {list(self.ids.keys())}")
                if hasattr(self.ids, 'project_overview_card'):
                    print(f"Available IDs in project_overview_card: {list(self.ids.project_overview_card.ids.keys())}")
                return
                
            stats_container.clear_widgets()
            
            if not self.current_project_id:
                # Show message when no project is selected
                from widgets.stat_card import StatCard
                no_project_card = StatCard(
                    title="No Project Selected",
                    value="Select a project above",
                    icon="database-off",
                    note="Choose a project to view statistics"
                )
                stats_container.add_widget(no_project_card)
                return
                
            stats = self.get_project_stats()
            print(f"Project stats: {stats}")
            
            if not stats:
                # Show error message when stats are not available
                from widgets.stat_card import StatCard
                error_card = StatCard(
                    title="Statistics Unavailable",
                    value="No data found",
                    icon="alert-circle",
                    note="Unable to load project statistics"
                )
                stats_container.add_widget(error_card)
                return
            
            # Import the existing StatCard widget
            from widgets.stat_card import StatCard
            
            stat_items = [
                ("Total Responses", f"{stats.get('total_responses', 0):,}", "database-outline", 
                 "Survey responses collected"),
                ("Questions", f"{stats.get('total_questions', 0)}", "help-circle-outline", 
                 "Questions in survey"),
                ("Completion Rate", f"{stats.get('completion_rate', 0):.1f}%", "chart-line", 
                 "Response completion rate"),
                ("Participants", f"{stats.get('unique_respondents', 0):,}", "account-group-outline", 
                 "Unique respondents"),
            ]
            
            for title, value, icon, note in stat_items:
                try:
                    stat_card = StatCard(
                        title=title,
                        value=value,
                        icon=icon,
                        note=note
                    )
                    stats_container.add_widget(stat_card)
                except Exception as card_error:
                    print(f"Error creating stat card for {title}: {card_error}")
                    
        except Exception as e:
            print(f"Error updating quick stats: {e}")
            # Show error message
            try:
                # Try to find stats_container through different paths
                stats_container = None
                if hasattr(self.ids, 'stats_container'):
                    stats_container = self.ids.stats_container
                elif hasattr(self.ids, 'project_overview_content') and hasattr(self.ids.project_overview_content.ids, 'stats_container'):
                    stats_container = self.ids.project_overview_content.ids.stats_container
                elif hasattr(self.ids, 'project_overview_card') and hasattr(self.ids.project_overview_card.ids, 'project_overview_content') and hasattr(self.ids.project_overview_card.ids.project_overview_content.ids, 'stats_container'):
                    stats_container = self.ids.project_overview_card.ids.project_overview_content.ids.stats_container
                
                if stats_container:
                    stats_container.clear_widgets()
                    from widgets.stat_card import StatCard
                    error_card = StatCard(
                        title="Error Loading Stats",
                        value="Please try again",
                        icon="alert-circle",
                        note="Failed to load project statistics"
                    )
                    stats_container.add_widget(error_card)
            except:
                pass

    def get_project_stats(self):
        """Get enhanced project statistics"""
        if not self.current_project_id:
            return {}
            
        try:
            # Try to get stats from analytics backend first
            stats = self.analytics_service.get_project_stats(self.current_project_id)
            
            if 'error' in stats:
                print(f"Error getting project stats from backend: {stats['error']}")
                # Fallback to database query
                stats = self._get_project_stats_from_db()
            
            if not stats:
                return {}
            
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
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'data_quality_score': min(100, completion_rate + 10) if completion_rate > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting project stats: {e}")
            # Fallback to database query
            return self._get_project_stats_from_db()

    def _get_project_stats_from_db(self):
        """Get project statistics directly from database as fallback"""
        try:
            app = App.get_running_app()
            conn = app.db_service.get_db_connection()
            
            if conn is None:
                return {}
                
            cursor = conn.cursor()
            
            # Get total responses
            cursor.execute("""
                SELECT COUNT(*) as total_responses
                FROM responses 
                WHERE project_id = ?
            """, (self.current_project_id,))
            total_responses = cursor.fetchone()['total_responses'] or 0
            
            # Get unique respondents
            cursor.execute("""
                SELECT COUNT(DISTINCT respondent_id) as unique_respondents
                FROM responses 
                WHERE project_id = ?
            """, (self.current_project_id,))
            unique_respondents = cursor.fetchone()['unique_respondents'] or 0
            
            # Get total questions
            cursor.execute("""
                SELECT COUNT(*) as total_questions
                FROM questions 
                WHERE project_id = ?
            """, (self.current_project_id,))
            total_questions = cursor.fetchone()['total_questions'] or 0
            
            return {
                'total_responses': total_responses,
                'total_questions': total_questions,
                'unique_respondents': unique_respondents
            }
            
        except Exception as e:
            print(f"Error getting project stats from database: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def get_analytics_info(self, category_key):
        """Get detailed information about an analytics category"""
        if category_key not in self.analytics_categories:
            return None
            
        category = self.analytics_categories[category_key]
        info = f"{category['name']}\n\n"
        info += f"{category['description']}\n\n"
        
        if isinstance(category['function_count'], int):
            info += f"Available Functions: {category['function_count']}\n\n"
        else:
            info += f"Type: {category['function_count']}\n\n"
            
        info += "Key Categories:\n"
        for cat in category['categories']:
            info += f"• {cat}\n"
            
        info += "\nKey Features:\n"
        for feature in category['key_features']:
            info += f"• {feature}\n"
            
        return info
    
    def show_descriptive_info(self):
        """Show information about descriptive analytics"""
        info = self.get_analytics_info('descriptive')
        if info:
            # For now, show as toast - could be enhanced with a popup dialog
            toast("Descriptive Analytics: 22 functions for statistical summaries and patterns")
        
    def show_qualitative_info(self):
        """Show information about qualitative analytics"""
        info = self.get_analytics_info('qualitative')
        if info:
            toast("Qualitative Analytics: 36 functions for text analysis and sentiment detection")
    
    def show_inferential_info(self):
        """Show information about inferential analytics"""
        info = self.get_analytics_info('inferential')
        if info:
            toast("Inferential Analytics: 89 functions for hypothesis testing and statistical inference")
            
    def show_auto_detection_info(self):
        """Show information about auto detection"""
        info = self.get_analytics_info('auto_detection')
        if info:
            toast("Auto Detection: AI-powered analysis recommendations and pattern recognition")
            
    def show_data_exploration_info(self):
        """Show information about data exploration"""
        info = self.get_analytics_info('data_exploration')
        if info:
            toast("Data Exploration: Interactive data browsing, filtering, and visualization tools")


    # Callback methods
    def show_project_selection_guide(self):
        """Show project selection guide"""
        toast("Select a project above to access analytics features")

    def navigate_to_projects(self):
        """Navigate to projects screen"""
        app = App.get_running_app()
        app.root.current = 'projects'
        toast("Opening Projects...")

    def on_window_resize(self, window, width, height):
        """Handle window resize"""
        self.update_responsive_layout()
        self.is_tablet = self._detect_tablet()

    def update_responsive_layout(self):
        """Update responsive layout"""
        try:
            window_width = Window.width
            window_height = Window.height
            
            if window_width < 800:
                stats_cols = 2
                card_spacing = dp(16)
            elif window_width < 1200:
                stats_cols = 4
                card_spacing = self.SPACING
            else:
                stats_cols = 4
                card_spacing = self.SPACING
                
            if hasattr(self.ids, 'stats_container'):
                container = self.ids.stats_container
                container.cols = stats_cols
                container.spacing = card_spacing
                
            if hasattr(self.ids, 'main_content'):
                if window_width > window_height:
                    self.ids.main_content.padding = [self.PADDING * 1.5, self.PADDING, self.PADDING * 1.5, self.PADDING]
                else:
                    self.ids.main_content.padding = [self.PADDING, self.PADDING * 1.5, self.PADDING, self.PADDING]
                
        except Exception as e:
            print(f"Error in responsive layout: {e}")
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.cols = 2