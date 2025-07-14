from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from utils.toast import toast
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
from kivy.core.window import Window
from kivy.clock import Clock
from widgets.forgot_password_popup import ForgotPasswordPopup
from widgets.responsive_layout import ResponsiveHelper
from kivy.metrics import dp

Builder.load_file("kv/login.kv")

class LoginScreen(MDScreen):
    is_authenticating = BooleanProperty(False)
    password_visible = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)
        
    def on_window_resize(self, window, width, height):
        """Handle window resize to update responsive elements"""
        Clock.schedule_once(lambda dt: self.update_responsive_elements(), 0.1)
        
    def update_responsive_elements(self):
        """Update responsive elements based on current screen size"""
        if not self.ids:
            return
            
        try:
            # Determine if we're on a tablet-sized screen
            is_tablet = Window.width > 600
            
            # Update button heights and font sizes based on screen size
            if is_tablet:
                button_height = dp(64)
                field_height = dp(64)
                button_font_size = "20sp"
                field_font_size = "18sp"
            else:
                button_height = dp(56)
                field_height = dp(56)
                button_font_size = "18sp"
                field_font_size = "16sp"
                
            # Update login button
            if hasattr(self.ids, 'login_button') and self.ids.login_button:
                self.ids.login_button.height = button_height
                self.ids.login_button.font_size = button_font_size
                
            # Update text fields
            if hasattr(self.ids, 'username') and self.ids.username:
                self.ids.username.height = field_height
                self.ids.username.font_size = field_font_size
                
            if hasattr(self.ids, 'password') and self.ids.password:
                self.ids.password.height = field_height
                self.ids.password.font_size = field_font_size
                
            print(f"Login: Updated responsive elements for {'tablet' if is_tablet else 'mobile'} view")
                
        except Exception as e:
            print(f"Error updating responsive elements: {e}")
    
    def clear_all_fields(self):
        """Clear all input fields to show placeholders"""
        field_ids = ['username', 'password']
        for field_id in field_ids:
            try:
                if hasattr(self.ids, field_id) and self.ids[field_id]:
                    self.ids[field_id].text = ""
                    # Force refresh of hint text
                    self.ids[field_id].focus = False
            except Exception as e:
                print(f"Error clearing field {field_id}: {e}")
    
    def validate_input(self, username, password):
        """Validate login input"""
        if not username:
            return False, "Please enter your username"
        if not password:
            return False, "Please enter your password"
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters"
        return True, ""
    
    def toggle_password_visibility(self):
        """Toggle password field visibility"""
        print("Toggling password visibility")
        self.password_visible = not self.password_visible
        try:
            if hasattr(self.ids, 'password') and self.ids.password:
                self.ids.password.password = not self.password_visible
                print("Password field updated:", self.ids.password.password)
        except Exception as e:
            print("Error updating password field:", e)
    
    def login(self):
        """Handle login with spinner and proper error handling"""
        try:
            user = self.ids.username.text.strip()
            pwd = self.ids.password.text.strip()
            
            # Validate input
            is_valid, error_message = self.validate_input(user, pwd)
            if not is_valid:
                toast(error_message)
                return
            
            # Start authentication process
            self.is_authenticating = True
            print("Login: Starting authentication process...")
            
            # Get auth service and authenticate
            app = MDApp.get_running_app()
            app.auth_service.authenticate(user, pwd, self._on_auth_complete)
            
        except Exception as e:
            print(f"Error during login: {e}")
            self.is_authenticating = False
            toast("An error occurred during login. Please try again.")
    
    def _on_auth_complete(self, result):
        """Handle authentication completion"""
        try:
            # Stop spinner
            self.is_authenticating = False
            
            if result.get('success'):
                # Authentication successful
                toast("Login successful!")
                app = MDApp.get_running_app()
                
                # Use the new login handler that properly sets up user context
                app.handle_successful_login()
            else:
                # Authentication failed
                error_type = result.get('error')
                message = result.get('message', 'Authentication failed')
                
                # Show appropriate error message
                if error_type == 'invalid_credentials':
                    toast("Invalid username or password")
                elif error_type == 'network_unavailable':
                    toast("No network connection. Please check your internet connection.")
                elif error_type == 'timeout':
                    toast("Request timed out. Please try again.")
                elif error_type == 'connection_error':
                    toast("Connection failed. Please check your internet connection.")
                elif error_type == 'server_error':
                    toast(f"Server error: {message}")
                else:
                    toast(f"Login failed: {message}")
                    
        except Exception as e:
            print(f"Error handling auth completion: {e}")
            self.is_authenticating = False
            toast("An error occurred. Please try again.")
    
    def on_signup(self):
        """Navigate to signup screen"""
        try:
            print("Navigating to signup screen")
            self.manager.transition.direction = "left"
            self.manager.current = "signup"
        except Exception as e:
            print(f"Error navigating to signup: {e}")

    def on_forgot_password(self):
        """Show forgot password popup"""
        try:
            print("Opening forgot password popup")
            popup = ForgotPasswordPopup()
            popup.open()
        except Exception as e:
            print(f"Error opening forgot password popup: {e}")
            toast("Forgot password feature is temporarily unavailable")
    
    def on_enter(self):
        """Called when screen is entered"""
        try:
            # Clear previous input and errors to show placeholders
            self.clear_all_fields()
            
            self.is_authenticating = False
            self.password_visible = False
            
            # Update responsive elements with slight delay
            Clock.schedule_once(lambda dt: self.update_responsive_elements(), 0.1)
            
        except Exception as e:
            print(f"Error in on_enter: {e}")
        
    def on_kv_post(self, base_widget):
        """Called after KV file is loaded"""
        try:
            super().on_kv_post(base_widget)
            
            # Update responsive elements
            Clock.schedule_once(lambda dt: self.update_responsive_elements(), 0.1)
            
            # Clear fields to show placeholders
            Clock.schedule_once(lambda dt: self.clear_all_fields(), 0.2)
            
        except Exception as e:
            print(f"Error in on_kv_post: {e}")