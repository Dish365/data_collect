from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
# Assuming you have these imports - adjust as needed
# from utils.cross_platform_toast import toast
# from widgets.forgot_password_popup import ForgotPasswordPopup

# Load the KV file
Builder.load_file("kv/login.kv")

class LoginScreen(MDScreen):
    is_authenticating = BooleanProperty(False)
    password_visible = BooleanProperty(False)
    
    def toggle_password_visibility(self):
        """Toggle password field visibility"""
        print("Toggling password visibility")
        self.password_visible = not self.password_visible
        try:
            # In KivyMD 2.0, the password field works differently
            password_field = self.ids.password
            password_field.password = not self.password_visible
            print(f"Password visibility set to: {not self.password_visible}")
        except Exception as e:
            print(f"Error updating password field: {e}")
    
    def login(self):
        """Handle login with spinner and proper error handling"""
        user = self.ids.username.text.strip()
        pwd = self.ids.password.text.strip()
        
        # Validate input
        if not user or not pwd:
            self.show_toast("Please enter both username and password")
            return
        
        # Start authentication process
        self.is_authenticating = True
        
        # Get auth service and authenticate
        app = MDApp.get_running_app()
        if hasattr(app, 'auth_service'):
            app.auth_service.authenticate(user, pwd, self._on_auth_complete)
        else:
            # Demo mode - simulate authentication
            from kivy.clock import Clock
            Clock.schedule_once(self._simulate_auth, 2.0)
    
    def _simulate_auth(self, dt):
        """Simulate authentication for demo purposes"""
        user = self.ids.username.text.strip()
        pwd = self.ids.password.text.strip()
        
        if user == "admin" and pwd == "password":
            self._on_auth_complete({'success': True})
        else:
            self._on_auth_complete({
                'success': False, 
                'error': 'invalid_credentials',
                'message': 'Invalid username or password'
            })
    
    def _on_auth_complete(self, result):
        """Handle authentication completion"""
        # Stop spinner
        self.is_authenticating = False
        
        if result.get('success'):
            # Authentication successful
            self.show_toast("Login successful!")
            app = MDApp.get_running_app()
            
            # Handle successful login
            if hasattr(app, 'handle_successful_login'):
                app.handle_successful_login()
            else:
                print("Login successful - implement navigation here")
        else:
            # Authentication failed
            error_type = result.get('error')
            message = result.get('message', 'Authentication failed')
            
            # Show appropriate error message
            if error_type == 'invalid_credentials':
                self.show_toast("Invalid username or password")
            elif error_type == 'network_unavailable':
                self.show_toast("No network connection. Please check your internet connection.")
            elif error_type == 'timeout':
                self.show_toast("Request timed out. Please try again.")
            elif error_type == 'connection_error':
                self.show_toast("Connection failed. Please check your internet connection.")
            elif error_type == 'server_error':
                self.show_toast(f"Server error: {message}")
            else:
                self.show_toast(f"Login failed: {message}")
    
    def show_toast(self, message):
        """Show toast message - fallback if toast utility not available"""
        try:
            # Try to use your toast utility if available
            from utils.cross_platform_toast import toast
            toast(message)
        except ImportError:
            # Fallback to using KivyMD snackbar
            try:
                from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
                from kivy.metrics import dp
                
                snackbar = MDSnackbar(
                    MDSnackbarText(text=message),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                )
                snackbar.open()
            except Exception as e:
                # Final fallback to print
                print(f"Toast: {message}")
    
    def on_signup(self):
        """Navigate to signup screen"""
        print("Sign up logic goes here")
        if self.manager:
            self.manager.transition.direction = "left"
            self.manager.current = "signup"

    def on_forgot_password(self):
        """Show forgot password popup"""
        print("Forgot password logic goes here")
        try:
            from widgets.forgot_password_popup import ForgotPasswordPopup
            popup = ForgotPasswordPopup()
            popup.open()
        except ImportError:
            self.show_toast("Forgot password feature coming soon")
    
    def on_enter(self):
        """Called when screen is entered"""
        # Clear previous input and errors
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.is_authenticating = False
        self.password_visible = False