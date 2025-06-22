from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file("kv/forgot_password_popup.kv")  # Adjust path if needed

class ForgotPasswordPopup(Popup):
    user_input = ObjectProperty(None)
    info_label = ObjectProperty(None)
    submit_callback = ObjectProperty(None)

    def on_submit(self):
        value = self.user_input.text.strip()
        if value:
            if self.submit_callback:
                self.submit_callback(value)
            self.dismiss()
        else:
            self.info_label.text = "Please enter a valid input!"
