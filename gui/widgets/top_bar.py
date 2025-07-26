from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.clock import Clock
import threading

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logout_dialog = None
        self.current_screen = "dashboard"
        self.notifications_data = {'unread_count': 0, 'notifications': []}
        self.notification_dialog = None
    
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
            if screen_name in ['dashboard', 'projects', 'analytics', 'data_collection', 'responses']:
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
                'data_collection': 'Data Collection',
                'responses': 'Responses',
                'sync': 'Sync',
                'login': 'Login',
                'signup': 'Sign Up'
            }
            
            title = screen_titles.get(screen_name, screen_name.title())
            self.set_title(title)
            
            # Show navigation feedback
            toast(f" Navigated to {title}")
    
    def set_current_screen(self, screen_name):
        """Set the current active screen for highlighting"""
        self.current_screen = screen_name
        # Could add visual highlighting logic here in the future
    
    def get_navigation_screens(self):
        """Get list of available navigation screens"""
        return ['dashboard', 'projects', 'analytics', 'data_collection', 'responses']
    
    def logout(self):
        """Show logout confirmation dialog"""
        if not self.logout_dialog:
            self.logout_dialog = MDDialog(
                title="Confirm Logout",
                text="Are you sure you want to logout? All unsaved data will be lost.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self._dismiss_logout_dialog
                    ),
                    MDRaisedButton(
                        text="LOGOUT",
                        on_release=self._confirm_logout
                    ),
                ],
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
        app.auth_service.logout()
        app.user_display_name = "Guest"
        
        # Show logout message
        toast("Logged out successfully")
        
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
                if unread_count > 0:
                    self.ids.notification_badge.text = str(min(unread_count, 99))  # Cap at 99
                    self.ids.notification_badge.opacity = 1
                else:
                    self.ids.notification_badge.opacity = 0
            
            # Update button color based on notifications
            if hasattr(self.ids, 'notification_button'):
                if unread_count > 0:
                    self.ids.notification_button.theme_icon_color = "Custom"
                    self.ids.notification_button.icon_color = [1, 0.5, 0, 1]  # Orange for notifications
                else:
                    self.ids.notification_button.theme_icon_color = "Primary"
                    
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
        """Show notifications dialog"""
        from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.label import MDLabel
        
        # Load fresh notifications
        self.load_notifications()
        
        # Create dialog content
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            size_hint_y=None,
            height="400dp",
            padding="16dp"
        )
        
        # Title
        title = MDLabel(
            text="Notifications",
            font_style="H6",
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(title)
        
        # Notifications list
        scroll = MDScrollView()
        notifications_list = MDList()
        
        notifications = self.notifications_data.get('notifications', [])
        
        if not notifications:
            empty_label = MDLabel(
                text="No new notifications",
                halign="center",
                theme_text_color="Hint",
                size_hint_y=None,
                height="40dp"
            )
            notifications_list.add_widget(empty_label)
        else:
            for notification in notifications:
                item = OneLineAvatarIconListItem(
                    text=notification['title'],
                    secondary_text=notification['message'][:100] + "..." if len(notification['message']) > 100 else notification['message']
                )
                
                # Add icon based on notification type
                icon_name = {
                    'team_invitation': 'account-plus',
                    'project_update': 'folder-edit',
                    'system_message': 'information',
                    'welcome': 'hand-wave'
                }.get(notification['type'], 'bell')
                
                item.add_widget(IconLeftWidget(icon=icon_name))
                notifications_list.add_widget(item)
        
        scroll.add_widget(notifications_list)
        content.add_widget(scroll)
        
        # Create dialog
        self.notification_dialog = MDDialog(
            title="Notifications",
            type="custom",
            content_cls=content,
            size_hint=(0.8, 0.7),
            buttons=[
                MDFlatButton(
                    text="MARK ALL READ",
                    on_release=self.mark_all_notifications_read
                ),
                MDFlatButton(
                    text="CLOSE",
                    on_release=self.close_notification_dialog
                )
            ]
        )
        
        self.notification_dialog.open()
    
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
            toast("All notifications marked as read")
            self.update_notification_badge(0)
            if self.notification_dialog:
                self.notification_dialog.dismiss()
        else:
            toast(f" Error: {message}")
    
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
