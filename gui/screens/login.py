from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.app import MDApp

Builder.load_file("kv/login.kv")

class LoginScreen(MDScreen):
    def login(self):
        user = self.ids.username.text
        pwd  = self.ids.password.text

        try:
            app = MDApp.get_running_app()
            # if auth_service isn't set, this will raise AttributeError
            if app.auth_service.authenticate(user, pwd):
                self.manager.current = "dashboard"
            else:
                toast("Invalid username or password")
        except Exception as e:
            # catch both missing auth_service and any other errors
            toast(f"Login error: {e}")
            # optionally log it
            print("Login exception:", e)

    def on_signup(self):
        print("Sign up logic goes here")
        self.manager.transition.direction = "left"
        self.manager.current = "signup"