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
from widgets.team_member_dialog import TeamMemberDialog


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
        
        # CLINICAL: Force immediate responsive layout
        self.update_responsive_layout()
        
        # CLINICAL: Force layout refresh after a short delay to ensure KV is loaded
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
            print("CLINICAL: Forcing layout refresh")
            
            # Force responsive layout update again
            self.update_responsive_layout()
            
            # Force all grids to re-layout
            if hasattr(self.ids, 'stats_grid'):
                self.ids.stats_grid.do_layout()
            if hasattr(self.ids, 'actions_grid'):
                self.ids.actions_grid.do_layout()
            if hasattr(self.ids, 'content_layout'):
                self.ids.content_layout.do_layout()
                
            print("CLINICAL: Layout refresh completed")
            
        except Exception as e:
            print(f"CLINICAL ERROR in layout refresh: {e}")

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
    
    def open_team_management(self):
        """Open team member management dialog"""
        try:
            team_dialog = TeamMemberDialog(
                dashboard_service=self.dashboard_service,
                callback=self.on_team_management_closed
            )
            team_dialog.open()
        except Exception as e:
            print(f"Error opening team management dialog: {e}")
    
    def on_team_management_closed(self):
        """Called when team management dialog is closed"""
        # Refresh dashboard stats to reflect any changes
        self.update_stats(show_loader=False)
    
    def update_team_member_card(self, team_members_count):
        """Update the team member card with enhanced information"""
        try:
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
                        team_info = self.dashboard_service.get_total_team_members_info()
                        if team_info and 'details' in team_info:
                            self.ids.team_members_card.note = team_info['details']
                        else:
                            self.ids.team_members_card.note = f"{count} team members - click to manage"
                except ValueError:
                    self.ids.team_members_card.note = "Click to manage team members"
        
        except Exception as e:
            print(f"Error updating team member card: {e}")
            self.ids.team_members_card.note = "Click to manage team members"
    
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
        self.update_team_member_card("Error")  # Use dedicated method
        
        # Clear notes for other cards
        self.ids.total_responses_card.note = ""
        self.ids.active_projects_card.note = ""
        self.ids.pending_sync_card.note = ""
        # Team members card note is handled by update_team_member_card
        
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
            
            # Team members note is set in the enhanced display section
            # Don't override it here unless there's an error
            team_members_count = stats.get('team_members', 'N/A')
            if team_members_count == 'N/A' or team_members_count == 'Error':
                self.ids.team_members_card.note = "Click to manage team members"
            
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
            
            # Enhanced team members display using dedicated method
            team_members_count = stats.get('team_members', 'N/A')
            self.update_team_member_card(team_members_count)

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
                        activity_icon=activity.get('icon'),
                        activity_type=activity.get('type', '')
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
            self.update_team_member_card("Loading...")  # Use dedicated method
            
            # Clear notes for other cards
            self.ids.total_responses_card.note = ""
            self.ids.active_projects_card.note = ""
            self.ids.pending_sync_card.note = ""
            # Team members card note is handled by update_team_member_card
            
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
    
    def on_window_resize(self, width, height):
        """Handle window resize for responsive layout adjustments"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            # Determine screen size category and orientation
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            print(f"Dashboard: Window resized to {width}x{height} - {category} {'landscape' if is_landscape else 'portrait'}")
            
            # Update responsive properties
            self.update_responsive_layout()
            
        except Exception as e:
            print(f"Error handling window resize in dashboard: {e}")
    
    def update_responsive_layout(self):
        """Update layout based on current screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            from kivy.core.window import Window
            
            # Get current window dimensions
            window_width = Window.width
            window_height = Window.height
            
            print(f"CLINICAL DEBUG: Window dimensions: {window_width}x{window_height}")
            
            # Update spacing and padding based on screen size
            if hasattr(self.ids, 'content_layout'):
                self.ids.content_layout.spacing = ResponsiveHelper.get_responsive_spacing()
                self.ids.content_layout.padding = ResponsiveHelper.get_responsive_padding()
            
            # CLINICAL FIX: Force single column for narrow windows
            if hasattr(self.ids, 'stats_container'):
                category = ResponsiveHelper.get_screen_size_category()
                is_landscape = ResponsiveHelper.is_landscape()
                
                print(f"CLINICAL DEBUG: Category={category}, Landscape={is_landscape}")
                
                # AGGRESSIVE WIDTH-BASED COLUMN CALCULATION
                # Each card needs absolute minimum 180dp width + 16dp spacing
                min_card_width = 180
                spacing = 16
                padding = 48  # Total left+right padding
                available_width = window_width - padding
                
                print(f"CLINICAL DEBUG: Available width for cards: {available_width}dp")
                
                # Calculate maximum possible columns with safety margin
                max_possible_cols = max(1, int(available_width / (min_card_width + spacing)))
                
                print(f"CLINICAL DEBUG: Max possible columns: {max_possible_cols}")
                
                # CLINICAL DECISION TREE - SUPER CONSERVATIVE FOR NARROW WINDOWS
                if window_width < 700:  # Very narrow - FORCE single column (increased from 600)
                    stats_cols = 1
                    actions_cols = 1
                    print("CLINICAL: FORCING single column for very narrow window")
                elif window_width < 1200:  # Narrow - FORCE single column for stats (increased from 1000)
                    stats_cols = 1
                    actions_cols = 2
                    print("CLINICAL: FORCING single stats column for narrow window")
                elif window_width < 1600:  # Medium - 2 columns max (increased from 1400)
                    stats_cols = min(2, max_possible_cols)
                    actions_cols = 2
                    print("CLINICAL: Using 2 columns max for medium window")
                else:  # Wide - use calculated columns but cap at 3 for actions
                    if is_landscape and category in ["tablet", "large_tablet"]:
                        stats_cols = min(4, max_possible_cols)
                        actions_cols = 3  # Max 3 columns for actions for better visual balance
                    else:
                        stats_cols = min(2, max_possible_cols)
                        actions_cols = 2
                    print("CLINICAL: Using calculated columns for wide window")
                
                # SAFETY CHECK - Never allow more columns than fit
                stats_cols = min(stats_cols, max_possible_cols, 4)
                stats_cols = max(stats_cols, 1)  # Never less than 1
                
                actions_cols = min(actions_cols, 3)  # Cap actions at 3 columns for better visual balance
                actions_cols = max(actions_cols, 1)
                
                print(f" Using {stats_cols} stats columns, {actions_cols} action columns")
                
                # Apply the calculated columns immediately
                self.set_stats_grid_columns(stats_cols)
                self.set_actions_grid_columns(actions_cols)
                
                # Update card sizes based on available space
                self.update_card_sizes(stats_cols, window_width, category)
            
        except Exception as e:
            print(f"CLINICAL ERROR in responsive layout: {e}")
            # EMERGENCY FALLBACK - Force single column
            self.set_stats_grid_columns(1)
            self.set_actions_grid_columns(1)

    def update_card_sizes(self, cols, window_width, category):
        """Update StatCard sizes based on layout and screen size"""
        try:
            print(f"CLINICAL: Updating card sizes for {cols} columns, width={window_width}")
            
            # CLINICAL CARD HEIGHT CALCULATION
            if window_width < 500:  # Very narrow
                card_height = 100  # Compact
            elif window_width < 800:  # Narrow
                card_height = 120
            elif cols == 1:  # Single column - can be taller
                card_height = 140
            elif cols == 2:  # Two columns
                card_height = 130
            elif cols == 3:  # Three columns
                card_height = 120
            else:  # Four columns
                card_height = 110
            
            print(f"CLINICAL: Setting card height to {card_height}dp")
            
            # Update all stat cards with clinical precision
            card_ids = ['total_responses_card', 'active_projects_card', 'pending_sync_card', 'team_members_card']
            for card_id in card_ids:
                if hasattr(self.ids, card_id):
                    card = getattr(self.ids, card_id)
                    
                    # FORCE HEIGHT UPDATE
                    card.size_hint_y = None
                    card.height = dp(card_height)
                    
                    # Try responsive height method if available
                    if hasattr(card, 'update_responsive_height'):
                        card.update_responsive_height(card_height)
                    
                    print(f"CLINICAL: Updated {card_id} height to {card_height}dp")
            
        except Exception as e:
            print(f"CLINICAL ERROR updating card sizes: {e}")

    def set_stats_grid_columns(self, cols):
        """Set the number of columns for the stats grid with clinical precision"""
        try:
            if hasattr(self.ids, 'stats_grid'):
                self.ids.stats_grid.cols = cols
                print(f"CLINICAL: Stats grid columns set to {cols}")
                
                # FORCE FULL WIDTH FOR SINGLE COLUMN
                if cols == 1:
                    card_ids = ['total_responses_card', 'active_projects_card', 'pending_sync_card', 'team_members_card']
                    for card_id in card_ids:
                        if hasattr(self.ids, card_id):
                            card = getattr(self.ids, card_id)
                            card.size_hint_x = 1  # Force full width
                            print(f"CLINICAL: Forced {card_id} to full width")
                
                # Force grid to re-layout immediately
                if hasattr(self.ids.stats_grid, 'do_layout'):
                    self.ids.stats_grid.do_layout()
                
                # Force parent layouts to update
                if hasattr(self.ids, 'stats_container'):
                    self.ids.stats_container.do_layout()
                if hasattr(self.ids, 'content_layout'):
                    self.ids.content_layout.do_layout()
                    
        except Exception as e:
            print(f"CLINICAL ERROR setting stats grid columns: {e}")
    
    def set_actions_grid_columns(self, cols):
        """Set the number of columns for the actions grid with clinical precision"""
        try:
            if hasattr(self.ids, 'actions_grid'):
                self.ids.actions_grid.cols = cols
                print(f"CLINICAL: Actions grid columns set to {cols}")
                
                # Update button heights based on columns for better visual balance
                button_height = dp(60) if cols <= 2 else dp(55)
                self.ids.actions_grid.row_default_height = button_height
                
                # Force grid to re-layout immediately
                if hasattr(self.ids.actions_grid, 'do_layout'):
                    self.ids.actions_grid.do_layout()
                
                # Force container to re-layout as well
                if hasattr(self.ids, 'actions_container'):
                    self.ids.actions_container.do_layout()
                    
        except Exception as e:
            print(f"CLINICAL ERROR setting actions grid columns: {e}") 