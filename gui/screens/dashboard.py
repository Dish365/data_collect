from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
import threading

# Import with fallbacks for better compatibility
try:
    from widgets.stat_card import StatCard
except ImportError:
    print("Warning: StatCard widget not found")
    StatCard = None

try:
    from widgets.top_bar import TopBar
except ImportError:
    print("Warning: TopBar widget not found")
    TopBar = None

try:
    from services.dashboard_service import DashboardService
except ImportError:
    print("Warning: DashboardService not found - using fallback")
    DashboardService = None

try:
    from widgets.activity_item import ActivityItem
except ImportError:
    print("Warning: ActivityItem widget not found")
    ActivityItem = None

try:
    from widgets.team_member_dialog import TeamMemberDialog
except ImportError:
    print("Warning: TeamMemberDialog not found")
    TeamMemberDialog = None

# KivyMD imports
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

Builder.load_file("kv/dashboard.kv")

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # Initialize dashboard service with fallback
        if DashboardService and hasattr(app, 'auth_service') and hasattr(app, 'db_service'):
            self.dashboard_service = DashboardService(app.auth_service, app.db_service)
        else:
            print("Warning: Dashboard service not available - using fallback mode")
            self.dashboard_service = None
            
        self.last_update_time = None
        self.auto_refresh_enabled = True

    def on_enter(self, *args):
        """Called when the screen is entered."""
        # Set top bar title and current screen
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Dashboard")
            self.ids.top_bar.set_current_screen("dashboard")
            
            # Start notification polling
            self.ids.top_bar.load_notifications()
            self.ids.top_bar.start_notification_polling()
        
        # Force immediate responsive layout
        self.update_responsive_layout()
        
        # Force layout refresh after a short delay to ensure KV is loaded
        Clock.schedule_once(self._force_layout_refresh, 0.1)
        
        # Initialize dashboard service for current user with retry logic
        if self._initialize_with_retry():
            self.update_stats()
        else:
            # Show error message if initialization completely fails
            self._handle_error("Failed to initialize dashboard. Please try logging out and back in.")
        
        # Schedule auto-refresh every 30 seconds if enabled
        if self.auto_refresh_enabled:
            Clock.schedule_interval(self.auto_refresh_stats, 30)

    def _force_layout_refresh(self, dt):
        """Force a complete layout refresh to ensure responsive layout is applied"""
        try:
            print("Dashboard: Forcing layout refresh")
            
            # Force responsive layout update again
            self.update_responsive_layout()
            
            # Force all grids to re-layout
            if hasattr(self.ids, 'stats_grid') and self.ids.stats_grid:
                self.ids.stats_grid.do_layout()
            if hasattr(self.ids, 'actions_grid') and self.ids.actions_grid:
                self.ids.actions_grid.do_layout()
            if hasattr(self.ids, 'content_layout') and self.ids.content_layout:
                self.ids.content_layout.do_layout()
                
            print("Dashboard: Layout refresh completed")
            
        except Exception as e:
            print(f"Error in layout refresh: {e}")

    def _initialize_with_retry(self, max_retries=3, delay=0.5):
        """Initialize dashboard with retry logic"""
        print(f"Starting dashboard initialization (max {max_retries} retries)")
        
        if not self.dashboard_service:
            print("Dashboard service not available")
            return False
        
        for attempt in range(max_retries):
            print(f"Dashboard initialization attempt {attempt + 1}")
            
            # First check if auth service has user data
            app = App.get_running_app()
            if not hasattr(app, 'auth_service') or not app.auth_service.is_authenticated():
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
        if self.dashboard_service and self.dashboard_service.initialize_for_user():
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
            if self.dashboard_service and self.dashboard_service.get_current_user_id():
                self.update_stats(show_loader=False)  # Silent refresh
            else:
                print("Warning: Lost user context during auto-refresh")

    def navigate_to(self, screen_name):
        if self.manager:
            self.manager.transition.direction = "left"  
            self.manager.current = screen_name
    
    def open_team_management(self):
        """Open team member management dialog"""
        try:
            if TeamMemberDialog and self.dashboard_service:
                team_dialog = TeamMemberDialog(
                    dashboard_service=self.dashboard_service,
                    callback=self.on_team_management_closed
                )
                team_dialog.open()
            else:
                self.show_toast("Team management not available")
        except Exception as e:
            print(f"Error opening team management dialog: {e}")
            self.show_toast("Error opening team management")
    
    def on_team_management_closed(self):
        """Called when team management dialog is closed"""
        # Refresh dashboard stats to reflect any changes
        self.update_stats(show_loader=False)
    
    def update_team_member_card(self, team_members_count):
        """Update the team member card with enhanced information"""
        try:
            if not hasattr(self.ids, 'team_members_card') or not self.ids.team_members_card:
                return
                
            self.ids.team_members_card.value = str(team_members_count)
            
            # Provide contextual information based on count
            if team_members_count == 'N/A' or team_members_count == 'Error':
                self.ids.team_members_card.note = "Click to manage team members"
            elif team_members_count == 'Loading...':
                self.ids.team_members_card.note = "Loading team information..."
            elif team_members_count == 'Offline':
                self.ids.team_members_card.note = "Offline - cached data"
            else:
                try:
                    count = int(team_members_count)
                    if count == 0:
                        self.ids.team_members_card.note = "No team members yet - click to add"
                    elif count == 1:
                        self.ids.team_members_card.note = "Just you - click to invite others"
                    else:
                        # Try to get detailed info
                        if self.dashboard_service:
                            team_info = self.dashboard_service.get_total_team_members_info()
                            if team_info and 'details' in team_info:
                                self.ids.team_members_card.note = team_info['details']
                            else:
                                self.ids.team_members_card.note = f"{count} team members - click to manage"
                        else:
                            self.ids.team_members_card.note = f"{count} team members - click to manage"
                except ValueError:
                    self.ids.team_members_card.note = "Click to manage team members"
        
        except Exception as e:
            print(f"Error updating team member card: {e}")
            if hasattr(self.ids, 'team_members_card') and self.ids.team_members_card:
                self.ids.team_members_card.note = "Click to manage team members"
    
    def show_loader(self, show=True):
        """Show/hide modern loading indicator"""
        try:
            if hasattr(self.ids, 'loading_card') and self.ids.loading_card:
                if show:
                    self.ids.loading_card.opacity = 1
                    if hasattr(self.ids, 'spinner') and self.ids.spinner:
                        self.ids.spinner.active = True
                else:
                    self.ids.loading_card.opacity = 0
                    if hasattr(self.ids, 'spinner') and self.ids.spinner:
                        self.ids.spinner.active = False
                        
            if hasattr(self.ids, 'main_scroll_view') and self.ids.main_scroll_view:
                self.ids.main_scroll_view.opacity = 0.3 if show else 1
        except Exception as e:
            print(f"Error updating loader: {e}")

    def show_toast(self, message):
        """Show toast message with fallback"""
        try:
            from utils.cross_platform_toast import toast
            toast(message)
        except ImportError:
            try:
                from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
                
                snackbar = MDSnackbar(
                    MDSnackbarText(text=message),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                )
                snackbar.open()
            except Exception:
                print(f"Toast: {message}")

    def update_stats(self, show_loader=True):
        """Fetches dashboard statistics in a background thread."""
        if not self.dashboard_service:
            self._handle_error("Dashboard service not available")
            return
            
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
            if self.dashboard_service:
                stats = self.dashboard_service.get_dashboard_stats()
                Clock.schedule_once(lambda dt: self._update_ui(stats))
            else:
                Clock.schedule_once(lambda dt: self._handle_error("Dashboard service not available"))
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            Clock.schedule_once(lambda dt: self._handle_error(str(e)))

    def _handle_error(self, error_message):
        """Handle error cases with modern UI updates"""
        print(f"Dashboard error: {error_message}")
        
        try:
            # Update stat cards with error state
            if hasattr(self.ids, 'total_responses_card') and self.ids.total_responses_card:
                self.ids.total_responses_card.value = "Error"
                self.ids.total_responses_card.note = ""
                
            if hasattr(self.ids, 'active_projects_card') and self.ids.active_projects_card:
                self.ids.active_projects_card.value = "Error"
                self.ids.active_projects_card.note = ""
                
            if hasattr(self.ids, 'pending_sync_card') and self.ids.pending_sync_card:
                self.ids.pending_sync_card.value = "Error"
                self.ids.pending_sync_card.note = ""
                
            self.update_team_member_card("Error")
            
            # Clear activity feed and show error message
            if hasattr(self.ids, 'activity_feed_layout') and self.ids.activity_feed_layout:
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
            
        except Exception as e:
            print(f"Error in error handler: {e}")
            self.show_loader(False)

    def _update_additional_info(self, stats):
        """Update additional information display"""
        try:
            # Get user permissions
            permissions = stats.get('user_permissions', {})
            
            can_manage = permissions.get('can_manage_users', False)
            can_create_projects = permissions.get('can_create_projects', True)
            can_collect_data = permissions.get('can_collect_data', True)
            
            # Update title based on permissions
            if can_manage:
                title = "Admin Dashboard"
            elif can_create_projects:
                title = "Researcher Dashboard"  
            else:
                title = "Field Worker Dashboard"
                
            if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
                self.ids.top_bar.set_title(title)
            
            # Update card notes to be more specific
            if hasattr(self.ids, 'total_responses_card') and self.ids.total_responses_card:
                self.ids.total_responses_card.note = "From your accessible projects"
                
            if hasattr(self.ids, 'active_projects_card') and self.ids.active_projects_card:
                if can_manage:
                    self.ids.active_projects_card.note = "All projects in system"
                else:
                    self.ids.active_projects_card.note = "Projects you created"
                    
            if hasattr(self.ids, 'pending_sync_card') and self.ids.pending_sync_card:
                self.ids.pending_sync_card.note = "Your pending operations"
            
            # Show warning for failed syncs
            failed_sync = stats.get('failed_sync', '0')
            if failed_sync and str(failed_sync) != '0':
                print(f"Warning: {failed_sync} failed sync operations")
                
        except Exception as e:
            print(f"Error updating additional info: {e}")

    def _update_ui(self, stats):
        """Updates the UI with new stats."""
        try:
            print(f"Updating UI with stats: {stats}")
            
            # Update stat cards with enhanced information
            if hasattr(self.ids, 'total_responses_card') and self.ids.total_responses_card:
                self.ids.total_responses_card.value = str(stats.get('total_respondents', 'N/A'))
                
            if hasattr(self.ids, 'active_projects_card') and self.ids.active_projects_card:
                self.ids.active_projects_card.value = str(stats.get('active_projects', 'N/A'))
                
            if hasattr(self.ids, 'pending_sync_card') and self.ids.pending_sync_card:
                self.ids.pending_sync_card.value = str(stats.get('pending_sync', 'N/A'))
            
            # Enhanced team members display using dedicated method
            team_members_count = stats.get('team_members', 'N/A')
            self.update_team_member_card(team_members_count)

            # Update activity feed
            if hasattr(self.ids, 'activity_feed_layout') and self.ids.activity_feed_layout:
                activity_feed_layout = self.ids.activity_feed_layout
                activity_feed_layout.clear_widgets()
                activity_feed = stats.get('activity_feed', [])
                
                if not activity_feed:
                    activity_feed_layout.add_widget(MDLabel(
                        text="No recent activity in your accessible projects.", 
                        halign="center", 
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(40)
                    ))
                else:
                    for activity in activity_feed:
                        if ActivityItem:
                            activity_feed_layout.add_widget(ActivityItem(
                                activity_text=activity.get('text'),
                                activity_time=activity.get('time'),
                                activity_icon=activity.get('icon'),
                                activity_type=activity.get('type', '')
                            ))
                        else:
                            # Fallback to simple label
                            activity_feed_layout.add_widget(MDLabel(
                                text=f"{activity.get('text', 'Activity')} - {activity.get('time', '')}",
                                size_hint_y=None,
                                height=dp(30),
                                theme_text_color="Secondary"
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
            if self.dashboard_service:
                self.dashboard_service.use_combined_endpoint = True
            
            # Clear current display
            self.show_loader(True)
            
            # Clear stat cards
            self._set_card_loading_state()
            
            # Clear activity feed
            if hasattr(self.ids, 'activity_feed_layout') and self.ids.activity_feed_layout:
                self.ids.activity_feed_layout.clear_widgets()
            
            # Reset update time
            self.last_update_time = None
            
            print("Dashboard reset completed")
            
        except Exception as e:
            print(f"Error resetting dashboard: {e}")

    def _set_card_loading_state(self):
        """Set all cards to loading state"""
        cards = ['total_responses_card', 'active_projects_card', 'pending_sync_card']
        
        for card_id in cards:
            if hasattr(self.ids, card_id) and getattr(self.ids, card_id):
                card = getattr(self.ids, card_id)
                card.value = "Loading..."
                card.note = ""
        
        self.update_team_member_card("Loading...")

    def force_refresh_for_user_change(self):
        """Force refresh dashboard when user context changes"""
        try:
            print("Forcing dashboard refresh for user change")
            
            # Reset for new user first
            self.reset_for_new_user()
            
            # Try to initialize and update immediately
            if self.dashboard_service and self.dashboard_service.initialize_for_user():
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
            
            if not self.dashboard_service:
                self._handle_error("Dashboard service not available")
                return
            
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
            user_id = self.dashboard_service.get_current_user_id() if self.dashboard_service else None
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
    
    def on_window_resize(self, width, height):
        """Handle window resize for responsive layout adjustments"""
        try:
            print(f"Dashboard: Window resized to {width}x{height}")
            
            # Update responsive properties
            self.update_responsive_layout()
            
        except Exception as e:
            print(f"Error handling window resize in dashboard: {e}")
    
    def update_responsive_layout(self):
        """Update layout based on current screen size"""
        try:
            from kivy.core.window import Window
            
            # Get current window dimensions
            window_width = Window.width
            window_height = Window.height
            
            print(f"Dashboard: Window dimensions: {window_width}x{window_height}")
            
            # Simple responsive spacing and padding
            if window_width < 600:
                spacing = 12
                padding = 16
            elif window_width < 1200:
                spacing = 16
                padding = 20
            else:
                spacing = 24
                padding = 24
            
            # Update spacing and padding based on screen size
            if hasattr(self.ids, 'content_layout') and self.ids.content_layout:
                self.ids.content_layout.spacing = spacing
                self.ids.content_layout.padding = [padding, padding/2, padding, padding]
            
            # Calculate responsive columns
            if hasattr(self.ids, 'stats_container') and self.ids.stats_container:
                # Simple responsive column calculation
                if window_width < 700:
                    stats_cols = 1
                    actions_cols = 1
                elif window_width < 1200:
                    stats_cols = 2
                    actions_cols = 2
                elif window_width < 1600:
                    stats_cols = 2
                    actions_cols = 3
                else:
                    stats_cols = 4
                    actions_cols = 4
                
                # Safety checks
                stats_cols = min(max(stats_cols, 1), 4)
                actions_cols = min(max(actions_cols, 1), 4)
                
                print(f"Dashboard: Using {stats_cols} stats columns, {actions_cols} action columns")
                
                # Apply the calculated columns
                self.set_stats_grid_columns(stats_cols)
                self.set_actions_grid_columns(actions_cols)
                
                # Update card sizes
                self.update_card_sizes(stats_cols, window_width)
            
        except Exception as e:
            print(f"Error in responsive layout: {e}")
            # Emergency fallback
            self.set_stats_grid_columns(1)
            self.set_actions_grid_columns(1)



    def update_card_sizes(self, cols, window_width):
        """Update StatCard sizes based on layout and screen size"""
        try:
            if window_width < 500:
                card_height = 100
            elif window_width < 800:
                card_height = 120
            elif cols == 1:
                card_height = 140
            elif cols == 2:
                card_height = 130
            elif cols == 3:
                card_height = 120
            else:
                card_height = 110
            
            print(f"Dashboard: Setting card height to {card_height}dp")
            
            # Update all stat cards
            card_ids = ['total_responses_card', 'active_projects_card', 'pending_sync_card', 'team_members_card']
            for card_id in card_ids:
                if hasattr(self.ids, card_id) and getattr(self.ids, card_id):
                    card = getattr(self.ids, card_id)
                    
                    # Force height update
                    card.size_hint_y = None
                    card.height = dp(card_height)
                    
                    # Try responsive height method if available
                    if hasattr(card, 'update_responsive_height'):
                        card.update_responsive_height(card_height)
            
        except Exception as e:
            print(f"Error updating card sizes: {e}")

    def set_stats_grid_columns(self, cols):
        """Set the number of columns for the stats grid"""
        try:
            if hasattr(self.ids, 'stats_grid') and self.ids.stats_grid:
                self.ids.stats_grid.cols = cols
                print(f"Dashboard: Stats grid columns set to {cols}")
                
                # Force full width for single column
                if cols == 1:
                    card_ids = ['total_responses_card', 'active_projects_card', 'pending_sync_card', 'team_members_card']
                    for card_id in card_ids:
                        if hasattr(self.ids, card_id) and getattr(self.ids, card_id):
                            card = getattr(self.ids, card_id)
                            card.size_hint_x = 1
                
                # Force layout refresh
                self.ids.stats_grid.do_layout()
                
                if hasattr(self.ids, 'stats_container') and self.ids.stats_container:
                    self.ids.stats_container.do_layout()
                    
        except Exception as e:
            print(f"Error setting stats grid columns: {e}")
    
    def set_actions_grid_columns(self, cols):
        """Set the number of columns for the actions grid"""
        try:
            if hasattr(self.ids, 'actions_grid') and self.ids.actions_grid:
                self.ids.actions_grid.cols = cols
                print(f"Dashboard: Actions grid columns set to {cols}")
                
                # Update button heights based on columns
                button_height = dp(64) if cols <= 2 else dp(60)
                self.ids.actions_grid.row_default_height = button_height
                
                # Force layout refresh
                self.ids.actions_grid.do_layout()
                
                if hasattr(self.ids, 'actions_container') and self.ids.actions_container:
                    self.ids.actions_container.do_layout()
                    
        except Exception as e:
            print(f"Error setting actions grid columns: {e}")