from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
import threading

# Updated imports for KivyMD 2.0
from kivymd.uix.dialog import (
    MDDialog, 
    MDDialogHeadlineText, 
    MDDialogSupportingText,
    MDDialogButtonContainer
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingIcon
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logout_dialog = None
        self.current_screen = "dashboard"
        self.notifications_data = {'unread_count': 0, 'notifications': []}
        self.notification_dialog = None
        self.navigation_menu = None
    
    def set_title(self, text):
        """Set the title text for the top bar"""
        if hasattr(self.ids, 'top_title'):
            self.ids.top_title.text = text
    
    def update_user_display(self):
        """Update the user display name in the top bar"""
        app = MDApp.get_running_app()
        if hasattr(self.ids, 'user_name'):
            self.ids.user_name.text = app.user_display_name
    
    def navigate_to_screen(self, screen_name):
        """Navigate to a specific screen with transition"""
        app = MDApp.get_running_app()
        if hasattr(app, 'root') and hasattr(app.root, 'current'):
            # Set transition direction based on screen hierarchy
            if screen_name in ['dashboard', 'projects', 'analytics', 'data_exploration', 'qualitative_analytics', 'data_collection', 'responses']:
                app.root.transition.direction = "left"
            else:
                app.root.transition.direction = "right"
                
            app.root.current = screen_name
            self.current_screen = screen_name
            
            # Update title based on screen
            screen_titles = {
                'dashboard': 'Dashboard',
                'projects': 'Projects', 
                'analytics': 'Analytics',
                'data_exploration': 'Data Exploration',
                'qualitative_analytics': 'Qualitative Analytics',
                'data_collection': 'Data Collection',
                'responses': 'Responses',
                'sync': 'Sync',
                'login': 'Login',
                'signup': 'Sign Up'
            }
            
            title = screen_titles.get(screen_name, screen_name.title())
            self.set_title(title)
            
            # Show navigation feedback
            self.show_toast(f"Navigated to {title}")
    
    def show_navigation_menu(self):
        """Show navigation menu for small screens"""
        navigation_items = [
            {
                "text": "Dashboard",
                "icon": "view-dashboard",
                "on_release": lambda x="dashboard": self._navigate_and_close_menu(x),
            },
            {
                "text": "Projects",
                "icon": "folder-multiple", 
                "on_release": lambda x="projects": self._navigate_and_close_menu(x),
            },
            {
                "text": "Analytics",
                "icon": "chart-line",
                "on_release": lambda x="analytics": self._navigate_and_close_menu(x),
            },
            {
                "text": "Data Exploration",
                "icon": "database-search",
                "on_release": lambda x="data_exploration": self._navigate_and_close_menu(x),
            },
            {
                "text": "Qualitative Analytics",
                "icon": "text-box",
                "on_release": lambda x="qualitative_analytics": self._navigate_and_close_menu(x),
            },
            {
                "text": "Data Collection",
                "icon": "clipboard-text",
                "on_release": lambda x="data_collection": self._navigate_and_close_menu(x),
            },
            {
                "text": "Responses",
                "icon": "format-list-bulleted",
                "on_release": lambda x="responses": self._navigate_and_close_menu(x),
            },
        ]
        
        if not self.navigation_menu:
            self.navigation_menu = MDDropdownMenu(
                caller=self.ids.hamburger_menu,
                items=navigation_items,
                width_mult=4,
            )
        else:
            self.navigation_menu.items = navigation_items
            
        self.navigation_menu.open()
    
    def _navigate_and_close_menu(self, screen_name):
        """Navigate to screen and close menu"""
        if self.navigation_menu:
            self.navigation_menu.dismiss()
        self.navigate_to_screen(screen_name)
    
    def show_toast(self, message):
        """Show toast message with KivyMD 2.0.1 snackbar"""
        try:
            from utils.cross_platform_toast import toast
            toast(message)
        except ImportError:
            try:
                snackbar = MDSnackbar(
                    MDSnackbarText(text=message),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                )
                snackbar.open()
            except Exception:
                print(f"Toast: {message}")
    
    def set_current_screen(self, screen_name):
        """Set the current active screen for highlighting"""
        self.current_screen = screen_name
    
    def get_navigation_screens(self):
        """Get list of available navigation screens"""
        return ['dashboard', 'projects', 'analytics', 'data_collection', 'responses']
    
    def logout(self):
        """Show logout confirmation dialog with KivyMD 2.0.1 syntax"""
        if not self.logout_dialog:
            self.logout_dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Confirm Logout"
                ),
                MDDialogSupportingText(
                    text="Are you sure you want to logout? All unsaved data will be lost."
                ),
                MDDialogButtonContainer(
                    Widget(),  # Spacer
                    MDButton(
                        MDButtonText(text="Cancel"),
                        style="text",
                        on_release=self._dismiss_logout_dialog
                    ),
                    MDButton(
                        MDButtonText(text="Logout"),
                        style="text",
                        on_release=self._confirm_logout
                    ),
                    spacing="8dp",
                ),
            )
        self.logout_dialog.open()
    
    def _dismiss_logout_dialog(self, instance):
        """Dismiss the logout confirmation dialog"""
        if self.logout_dialog:
            self.logout_dialog.dismiss()
    
    def _confirm_logout(self, instance):
        """Handle confirmed logout"""
        if self.logout_dialog:
            self.logout_dialog.dismiss()
        
        app = MDApp.get_running_app()
        
        # Logout from auth service
        if hasattr(app, 'auth_service'):
            app.auth_service.logout()
        app.user_display_name = "Guest"
        
        # Show logout message
        self.show_toast("Logged out successfully")
        
        # Stop notification polling
        self.stop_notification_polling()
        
        # Navigate back to login screen
        app.root.transition.direction = "right"
        app.root.current = "login"
        self.current_screen = "login"
    
    def update_notification_badge(self, unread_count=0):
        """Update the notification badge count"""
        try:
            if hasattr(self.ids, 'notification_badge'):
                badge = self.ids.notification_badge
                if unread_count > 0:
                    badge.text = str(min(unread_count, 99))  # Cap at 99
                    badge.opacity = 1
                else:
                    badge.text = "0"
                    badge.opacity = 0
            
            # Update button icon based on notifications
            if hasattr(self.ids, 'notification_button'):
                button = self.ids.notification_button
                if unread_count > 0:
                    button.icon = "bell"  # Filled bell for notifications
                    button.icon_color = [1, 0.7, 0, 1]  # Orange for notifications
                else:
                    button.icon = "bell-outline"  # Outline bell for no notifications
                    button.icon_color = [1, 1, 1, 0.9]  # White default
                    
        except Exception as e:
            print(f"Error updating notification badge: {e}")
    
    def load_notifications(self, dt=None):
        """Load user notifications in background"""
        def load_in_thread():
            try:
                app = MDApp.get_running_app()
                if hasattr(app, 'dashboard_service'):
                    # Check if user is still authenticated
                    if hasattr(app, 'auth_service') and app.auth_service.is_authenticated():
                        notifications_data = app.dashboard_service.get_notifications()
                        Clock.schedule_once(lambda dt: self.handle_notifications_loaded(notifications_data))
                    else:
                        # User not authenticated, clear notifications
                        Clock.schedule_once(lambda dt: self.handle_notifications_loaded({'unread_count': 0, 'notifications': []}))
                else:
                    print("Dashboard service not available for notifications")
                    Clock.schedule_once(lambda dt: self.handle_notifications_loaded({'unread_count': 0, 'notifications': []}))
            except Exception as e:
                print(f"Error loading notifications: {e}")
                Clock.schedule_once(lambda dt: self.handle_notifications_loaded({'unread_count': 0, 'notifications': []}))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def handle_notifications_loaded(self, notifications_data):
        """Handle loaded notifications"""
        self.notifications_data = notifications_data
        self.update_notification_badge(notifications_data.get('unread_count', 0))
    
    def show_notifications(self):
        """Show notifications dialog with modern KivyMD 2.0.1 design"""
        # Load fresh notifications
        self.load_notifications()
        
        # Create notifications list content
        scroll = MDScrollView()
        notifications_list = MDList()
        
        notifications = self.notifications_data.get('notifications', [])
        
        if not notifications:
            empty_label = MDLabel(
                text="No new notifications",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="40dp"
            )
            notifications_list.add_widget(empty_label)
        else:
            for notification in notifications:
                item = MDListItem(
                    MDListItemLeadingIcon(
                        icon=self._get_notification_icon(notification.get('type', 'bell'))
                    ),
                    MDListItemHeadlineText(
                        text=notification['title']
                    ),
                    MDListItemSupportingText(
                        text=notification['message'][:100] + "..." if len(notification['message']) > 100 else notification['message']
                    )
                )
                notifications_list.add_widget(item)
        
        scroll.add_widget(notifications_list)
        
        # Create dialog with KivyMD 2.0.1 syntax
        self.notification_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Notifications"
            ),
            MDDialogSupportingText(
                text=f"You have {len(notifications)} notification{'s' if len(notifications) != 1 else ''}"
            ),
            scroll,
            MDDialogButtonContainer(
                Widget(),  # Spacer
                MDButton(
                    MDButtonText(text="Mark All Read"),
                    style="text",
                    on_release=self.mark_all_notifications_read
                ),
                MDButton(
                    MDButtonText(text="Close"),
                    style="text", 
                    on_release=self.close_notification_dialog
                ),
                spacing="8dp",
            ),
        )
        
        self.notification_dialog.open()
    
    def _get_notification_icon(self, notification_type):
        """Get icon name based on notification type"""
        return {
            'team_invitation': 'account-plus',
            'project_update': 'folder-edit',
            'system_message': 'information',
            'welcome': 'hand-wave'
        }.get(notification_type, 'bell')
    
    def mark_all_notifications_read(self, *args):
        """Mark all notifications as read"""
        def mark_in_thread():
            try:
                app = MDApp.get_running_app()
                if hasattr(app, 'dashboard_service'):
                    success, message = app.dashboard_service.mark_all_notifications_read()
                    Clock.schedule_once(lambda dt: self.handle_mark_all_result(success, message))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.handle_mark_all_result(False, str(e)))
        
        threading.Thread(target=mark_in_thread, daemon=True).start()
    
    def handle_mark_all_result(self, success, message):
        """Handle mark all notifications result"""
        if success:
            self.show_toast("All notifications marked as read")
            self.update_notification_badge(0)
            if self.notification_dialog:
                self.notification_dialog.dismiss()
        else:
            self.show_toast(f"Error: {message}")
    
    def close_notification_dialog(self, *args):
        """Close notification dialog"""
        if self.notification_dialog:
            self.notification_dialog.dismiss()
    
    def start_notification_polling(self):
        """Start periodic notification checking"""
        # Check notifications every 30 seconds
        Clock.schedule_interval(self.load_notifications, 30)
        
        # Load initial notifications
        self.load_notifications()
    
    def stop_notification_polling(self):
        """Stop notification polling"""
        # Unschedule the notification loading
        Clock.unschedule(self.load_notifications)
        
        # Reset notification badge
        self.update_notification_badge(0)
        
        # Clear notifications data
        self.notifications_data = {'unread_count': 0, 'notifications': []}