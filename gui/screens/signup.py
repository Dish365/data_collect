from kivymd.uix.screen import MDScreen
from kivy.lang import Builder


Builder.load_file("kv/signup.kv")

class SignUpScreen(MDScreen):
    def signup(self):
        first_name    = self.ids.first_name.text.strip()
        last_name    = self.ids.last_name.text.strip()
        email = self.ids.email.text.strip()
        password   = self.ids.password.text
        confirm_password  = self.ids.confirm_password.text
        app   = self.manager.parent

        # basic client-side checks
        if not (first_name and last_name and email and password and confirm_password):
            print("Please fill all fields")
            return
        if password != confirm_password:
            print("Passwords do not match")
            return

        # call your auth service (you’d need a register method)
        if app.auth_service.register(first_name, last_name, email, password):
            # on success, go to login or dashboard
            self.manager.current = "login"
        else:
            print("Registration failed")

    def on_login(self):
        print("Sign up logic goes here")
        self.manager.transition.direction = "right"
        self.manager.current = "login"