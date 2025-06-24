from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from widgets.forgot_password_popup import ForgotPasswordPopup

Builder.load_file("kv/login.kv")

class LoginScreen(MDScreen):
    is_authenticating = BooleanProperty(False)
    
    def login(self):
        """Handle login with spinner and proper error handling"""
        user = self.ids.username.text.strip()
        pwd = self.ids.password.text.strip()
        
        # Validate input
        if not user or not pwd:
            toast("Please enter both username and password")
            return
        
        # Start authentication process
        self.is_authenticating = True
        
        # Get auth service and authenticate
        app = MDApp.get_running_app()
        app.auth_service.authenticate(user, pwd, self._on_auth_complete)
    
    def _on_auth_complete(self, result):
        """Handle authentication completion"""
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
    
    def on_signup(self):
        """Navigate to signup screen"""
        print("Sign up logic goes here")
        self.manager.transition.direction = "left"
        self.manager.current = "signup"

    def on_forgot_password(self):
        """Show forgot password popup"""
        print("Forgot password logic goes here")
        popup = ForgotPasswordPopup()
        popup.open()
    
    def on_enter(self):
        """Called when screen is entered"""
        # Clear previous input and errors
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.is_authenticating = False