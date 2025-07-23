from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logout_dialog = None
        self.current_screen = "dashboard"
    
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
                'dashboard': '📊 Dashboard',
                'projects': '📁 Projects', 
                'analytics': '📈 Analytics',
                'data_collection': '📋 Data Collection',
                'responses': '📄 Responses',
                'sync': '🔄 Sync',
                'login': '🔐 Login',
                'signup': '📝 Sign Up'
            }
            
            title = screen_titles.get(screen_name, screen_name.title())
            self.set_title(title)
            
            # Show navigation feedback
            toast(f"📍 Navigated to {title}")
    
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
        toast("✅ Logged out successfully")
        
        # Navigate back to login screen
        app.root.transition.direction = "right"
        app.root.current = "login"
        self.current_screen = "login"
