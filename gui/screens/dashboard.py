from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from widgets.stat_card import StatCard
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.core.window import Window
from widgets.top_bar import TopBar
from services.dashboard_service import DashboardService
import threading
from kivy.clock import Clock
from widgets.activity_item import ActivityItem
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton


Builder.load_file("kv/dashboard.kv")


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.dashboard_service = DashboardService(app.auth_service, app.db_service)
        self.last_update_time = None
        self.auto_refresh_enabled = True

    def on_enter(self, *args):
        """Called when the screen is entered."""
        self.ids.top_bar.set_title("Dashboard")
        
        # Initialize dashboard service for current user with retry logic
        if self._initialize_with_retry():
            self.update_stats()
        else:
            # Show error message if initialization completely fails
            self._handle_error("Failed to initialize dashboard. Please try logging out and back in.")
        
        # Schedule auto-refresh every 30 seconds if enabled
        if self.auto_refresh_enabled:
            Clock.schedule_interval(self.auto_refresh_stats, 30)

    def _initialize_with_retry(self, max_retries=3, delay=0.5):
        """Initialize dashboard with retry logic"""
        print(f"Starting dashboard initialization (max {max_retries} retries)")
        
        for attempt in range(max_retries):
            print(f"Dashboard initialization attempt {attempt + 1}")
            
            # First check if auth service has user data
            app = App.get_running_app()
            if not app.auth_service.is_authenticated():
                print(f"Attempt {attempt + 1}: User not authenticated")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(delay)
                    delay *= 1.5
                continue
            
            # Try to initialize dashboard service
            if self.dashboard_service.initialize_for_user():
                print(f"Dashboard initialized successfully on attempt {attempt + 1}")
                return True
            
            if attempt < max_retries - 1:  # Don't delay on the last attempt
                print(f"Dashboard initialization attempt {attempt + 1} failed, retrying in {delay}s...")
                import time
                time.sleep(delay)
                delay *= 1.5
        
        print("Dashboard initialization failed after all retries")
        return False

    def _delayed_init(self, dt):
        """Delayed initialization if user context wasn't ready initially"""
        if self.dashboard_service.initialize_for_user():
            self.update_stats()
        else:
            print("Warning: Could not initialize dashboard even after delay")
            # Show error state or try to get basic stats anyway
            self._handle_error("User authentication not ready. Please try refreshing.")
    
    def on_leave(self, *args):
        """Called when the screen is left."""
        # Unschedule auto-refresh
        Clock.unschedule(self.auto_refresh_stats)
        # Also unschedule any delayed init
        Clock.unschedule(self._delayed_init)

    def auto_refresh_stats(self, dt):
        """Auto-refresh stats if screen is still active"""
        if self.manager.current == "dashboard":
            # Ensure user context is still available
            if self.dashboard_service.get_current_user_id():
                self.update_stats(show_loader=False)  # Silent refresh
            else:
                print("Warning: Lost user context during auto-refresh")

    def navigate_to(self, screen_name):
        self.manager.transition.direction = "left"  
        self.manager.current = screen_name
    
    def show_loader(self, show=True):
        self.ids.spinner.active = show
        self.ids.main_scroll_view.opacity = 0 if show else 1

    def update_stats(self, show_loader=True):
        """Fetches dashboard statistics in a background thread."""
        # Verify user context before updating
        user_id = self.dashboard_service.get_current_user_id()
        if not user_id:
            print("Warning: No user context available for stats update")
            if show_loader:
                self._handle_error("User not authenticated. Please log in again.")
            return
            
        if show_loader:
            self.show_loader(True)
        threading.Thread(target=self._update_in_thread, daemon=True).start()

    def refresh_dashboard(self):
        """Manual refresh of dashboard data"""
        print("Manual dashboard refresh requested")
        self.force_complete_refresh()

    def _update_in_thread(self):
        """Background task to get stats."""
        try:
            stats = self.dashboard_service.get_dashboard_stats()
            Clock.schedule_once(lambda dt: self._update_ui(stats))
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            Clock.schedule_once(lambda dt: self._handle_error(str(e)))

    def _handle_error(self, error_message):
        """Handle error cases"""
        print(f"Dashboard error: {error_message}")
        # Show fallback data or error message
        self.ids.total_responses_card.value = "Error"
        self.ids.active_projects_card.value = "Error"
        self.ids.pending_sync_card.value = "Error"
        self.ids.team_members_card.value = "Error"
        
        # Clear notes
        self.ids.total_responses_card.note = ""
        self.ids.active_projects_card.note = ""
        self.ids.pending_sync_card.note = ""
        self.ids.team_members_card.note = ""
        
        # Clear activity feed and show error message
        activity_feed_layout = self.ids.activity_feed_layout
        activity_feed_layout.clear_widgets()
        activity_feed_layout.add_widget(MDLabel(
            text=f"Error loading data: {error_message}", 
            halign="center", 
            theme_text_color="Error",
            size_hint_y=None,
            height=dp(40)
        ))
        
        self.show_loader(False)

    def _update_additional_info(self, stats):
        """Update additional information display"""
        try:
            # Get user permissions
            permissions = stats.get('user_permissions', {})
            
            # You can add logic here to show/hide UI elements based on permissions
            can_manage = permissions.get('can_manage_users', False)
            can_create_projects = permissions.get('can_create_projects', True)
            can_collect_data = permissions.get('can_collect_data', True)
            
            # Example: Update title based on permissions
            if can_manage:
                title = "Admin Dashboard"
            elif can_create_projects:
                title = "Researcher Dashboard"  
            else:
                title = "Field Worker Dashboard"
                
            self.ids.top_bar.set_title(title)
            
            # Update card notes to be more specific
            # Total responses - from projects user has access to
            self.ids.total_responses_card.note = "From your accessible projects"
            
            # Active projects - projects user can see
            if can_manage:
                self.ids.active_projects_card.note = "All projects in system"
            else:
                self.ids.active_projects_card.note = "Projects you created"
            
            # Pending sync - user's sync operations
            self.ids.pending_sync_card.note = "Your pending operations"
            
            # Team members - people who worked on accessible projects
            self.ids.team_members_card.note = "Active in your projects"
            
            # Show additional stats as tooltips or helper text
            failed_sync = stats.get('failed_sync', '0')
            if failed_sync != '0' and failed_sync != 0:
                print(f"Warning: {failed_sync} failed sync operations")
                
        except Exception as e:
            print(f"Error updating additional info: {e}")

    def _update_ui(self, stats):
        """Updates the UI with new stats."""
        try:
            # Update stat cards with enhanced information
            self.ids.total_responses_card.value = stats.get('total_respondents', 'N/A')
            self.ids.active_projects_card.value = stats.get('active_projects', 'N/A')
            self.ids.pending_sync_card.value = stats.get('pending_sync', 'N/A')
            self.ids.team_members_card.value = stats.get('team_members', 'N/A')

            # Update additional stats if available
            failed_sync = stats.get('failed_sync', '0')
            recent_responses = stats.get('recent_responses', '0')
            completion_rate = stats.get('completion_rate', 'N/A')
            
            # Show warning for failed syncs
            if failed_sync and str(failed_sync) != '0':
                print(f"Note: {failed_sync} sync operations have failed")
                # Could add a visual indicator here
            
            # Update activity feed
            activity_feed_layout = self.ids.activity_feed_layout
            activity_feed_layout.clear_widgets()
            activity_feed = stats.get('activity_feed', [])
            
            if not activity_feed:
                activity_feed_layout.add_widget(MDLabel(
                    text="No recent activity in your accessible projects.", 
                    halign="center", 
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=dp(40)
                ))
            else:
                for activity in activity_feed:
                    activity_feed_layout.add_widget(ActivityItem(
                        activity_text=activity.get('text'),
                        activity_time=activity.get('time'),
                        activity_icon=activity.get('icon')
                    ))
                    
            # Show additional information if available
            self._update_additional_info(stats)
            
            # Update last refresh time
            from datetime import datetime
            self.last_update_time = datetime.now()
            
            self.show_loader(False)
            
            # Log summary for debugging
            print(f"Dashboard updated - Projects: {stats.get('active_projects', 'N/A')}, "
                  f"Responses: {stats.get('total_respondents', 'N/A')}, "
                  f"Pending Sync: {stats.get('pending_sync', 'N/A')}, "
                  f"Team: {stats.get('team_members', 'N/A')}")
            
            # Debug the actual values being set
            print(f"Debug - Setting card values:")
            print(f"  total_responses_card.value = '{stats.get('total_respondents', 'N/A')}'")
            print(f"  active_projects_card.value = '{stats.get('active_projects', 'N/A')}'")
            print(f"  pending_sync_card.value = '{stats.get('pending_sync', 'N/A')}'")
            print(f"  team_members_card.value = '{stats.get('team_members', 'N/A')}'")
            
            # Force update the card display methods
            self.ids.total_responses_card.update_value(stats.get('total_respondents', 'N/A'))
            self.ids.active_projects_card.update_value(stats.get('active_projects', 'N/A'))
            self.ids.pending_sync_card.update_value(stats.get('pending_sync', 'N/A'))
            self.ids.team_members_card.update_value(stats.get('team_members', 'N/A'))
            
        except Exception as e:
            print(f"Error updating UI: {e}")
            self._handle_error(f"UI update error: {str(e)}")

    def reset_for_new_user(self):
        """Reset dashboard state for a new user login"""
        try:
            print("Resetting dashboard for new user")
            
            # Cancel any pending operations
            Clock.unschedule(self.auto_refresh_stats)
            Clock.unschedule(self._delayed_init)
            
            # Reset dashboard service state
            self.dashboard_service.use_combined_endpoint = True
            
            # Clear current display
            self.show_loader(True)
            
            # Clear stat cards
            self.ids.total_responses_card.value = "Loading..."
            self.ids.active_projects_card.value = "Loading..."
            self.ids.pending_sync_card.value = "Loading..."
            self.ids.team_members_card.value = "Loading..."
            
            # Clear notes
            self.ids.total_responses_card.note = ""
            self.ids.active_projects_card.note = ""
            self.ids.pending_sync_card.note = ""
            self.ids.team_members_card.note = ""
            
            # Clear activity feed
            activity_feed_layout = self.ids.activity_feed_layout
            activity_feed_layout.clear_widgets()
            
            # Reset update time
            self.last_update_time = None
            
            print("Dashboard reset completed")
            
        except Exception as e:
            print(f"Error resetting dashboard: {e}")

    def force_refresh_for_user_change(self):
        """Force refresh dashboard when user context changes"""
        try:
            print("Forcing dashboard refresh for user change")
            
            # Reset for new user first
            self.reset_for_new_user()
            
            # Try to initialize and update immediately
            if self.dashboard_service.initialize_for_user():
                self.update_stats(show_loader=True)
            else:
                print("Warning: Could not initialize dashboard service during force refresh")
                # Schedule a delayed retry
                Clock.schedule_once(self._delayed_init, 1.0)
                
        except Exception as e:
            print(f"Error during force refresh: {e}")

    def force_complete_refresh(self):
        """Force a complete refresh of all dashboard data"""
        try:
            print("Performing complete dashboard refresh")
            
            # Reset dashboard service
            self.dashboard_service.use_combined_endpoint = True
            
            # Re-initialize for current user
            if self.dashboard_service.initialize_for_user():
                # Clear and reload everything
                self.reset_for_new_user()
                self.update_stats(show_loader=True)
            else:
                self._handle_error("Could not refresh dashboard - please try logging out and back in")
                
        except Exception as e:
            print(f"Error during complete refresh: {e}")
            self._handle_error(f"Refresh failed: {str(e)}")

    def get_dashboard_summary(self):
        """Get a summary of current dashboard state for other screens"""
        try:
            user_id = self.dashboard_service.get_current_user_id()
            return {
                'last_update': self.last_update_time,
                'auto_refresh': self.auto_refresh_enabled,
                'stats_available': True,
                'user_id': user_id,
                'initialized': user_id is not None
            }
        except:
            return {
                'last_update': None,
                'auto_refresh': False,
                'stats_available': False,
                'user_id': None,
                'initialized': False
            }

    def toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        if self.auto_refresh_enabled:
            Clock.schedule_interval(self.auto_refresh_stats, 30)
        else:
            Clock.unschedule(self.auto_refresh_stats)
        print(f"Auto-refresh {'enabled' if self.auto_refresh_enabled else 'disabled'}") 