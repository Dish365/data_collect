from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Title
        title = Label(
            text='Research Data Collector',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24)
        )
        layout.add_widget(title)
        
        # Username input
        self.username = TextInput(
            multiline=False,
            hint_text='Username',
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.username)
        
        # Password input
        self.password = TextInput(
            multiline=False,
            hint_text='Password',
            password=True,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.password)
        
        # Login button
        login_btn = Button(
            text='Login',
            size_hint_y=None,
            height=dp(50),
            on_press=self.login
        )
        layout.add_widget(login_btn)
        
        # Add layout to screen
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username.text
        password = self.password.text
        
        # Get the app instance
        app = self.manager.get_screen('login').parent
        
        # Call auth service
        if app.auth_service.authenticate(username, password):
            # Switch to dashboard on successful login
            self.manager.current = 'dashboard'
        else:
            # Show error message (you might want to add a proper error display)
            print("Login failed") 