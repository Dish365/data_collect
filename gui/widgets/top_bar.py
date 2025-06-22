from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def set_title(self, text):
        self.ids.top_title.text = text
    
    def update_user_info(self):
        """Update user information from auth service"""
        app = MDApp.get_running_app()
        if app.auth_service.is_authenticated():
            user_data = app.auth_service.get_user_data()
            if user_data:
                # Try to get username or email
                username = user_data.get('username', '')
                first_name = user_data.get('first_name', '')
                last_name = user_data.get('last_name', '')
                
                if first_name and last_name:
                    display_name = f"{first_name} {last_name}"
                elif first_name:
                    display_name = first_name
                elif username:
                    display_name = username
                else:
                    display_name = "User"
                
                self.ids.user_name.text = display_name
            else:
                self.ids.user_name.text = "User"
        else:
            self.ids.user_name.text = "Guest"
    
    def logout(self):
        """Handle user logout"""
        app = MDApp.get_running_app()
        
        # Logout from auth service
        app.auth_service.logout()
        
        # Show logout message
        toast("Logged out successfully")
        
        # Navigate back to login screen
        app.root.transition.direction = "right"
        app.root.current = "login"
