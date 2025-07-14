from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from utils.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText
from kivy.core.window import Window
from widgets.responsive_layout import ResponsiveHelper

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logout_dialog = None
        Window.bind(on_resize=self.on_window_resize)
    
    def on_window_resize(self, window, width, height):
        """Handle window resize to update responsive elements"""
        self.update_responsive_elements()
        
    def update_responsive_elements(self):
        """Update responsive elements based on current screen size"""
        if not self.ids:
            return
            
        # Update topbar height based on screen size
        if Window.width > 600:
            self.height = "64dp"
            title_font_size = "20sp"
            user_font_size = "16sp"
        else:
            self.height = "56dp"
            title_font_size = "18sp"
            user_font_size = "14sp"
            
        # Update title font size
        if hasattr(self.ids, 'top_title'):
            self.ids.top_title.font_size = title_font_size
            
        # Update user name font size
        if hasattr(self.ids, 'user_name'):
            self.ids.user_name.font_size = user_font_size
    
    def set_title(self, text):
        """Set the title text for the top bar"""
        if hasattr(self.ids, 'top_title'):
            self.ids.top_title.text = text
    
    def update_user_display(self):
        """Update the user display name in the top bar"""
        app = MDApp.get_running_app()
        if hasattr(self.ids, 'user_name'):
            self.ids.user_name.text = app.user_display_name
    
    def show_logout_dialog(self):
        """Show logout confirmation dialog"""
        if not self.logout_dialog:
            # Create dialog content
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            
            content = MDBoxLayout(
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="100dp"
            )
            
            content.add_widget(MDLabel(
                text="Are you sure you want to logout?",
                theme_text_color="Primary",
                halign="center"
            ))
            
            # Create buttons
            cancel_button = MDButton(
                MDButtonText(text="CANCEL"),
                style="text",
                on_release=self.close_logout_dialog
            )
            
            logout_button = MDButton(
                MDButtonText(text="LOGOUT"),
                style="elevated",
                on_release=self.handle_logout
            )
            
            self.logout_dialog = MDDialog(
                auto_dismiss=False
            )
            self.logout_dialog.add_widget(content)
            
            # Add buttons to dialog
            button_layout = MDBoxLayout(
                orientation="horizontal",
                spacing="8dp",
                size_hint_y=None,
                height="48dp",
                adaptive_width=True,
                pos_hint={"center_x": 0.5}
            )
            button_layout.add_widget(cancel_button)
            button_layout.add_widget(logout_button)
            
            content.add_widget(button_layout)
            
        self.logout_dialog.open()
    
    def close_logout_dialog(self, *args):
        """Close the logout dialog"""
        if self.logout_dialog:
            self.logout_dialog.dismiss()
    
    def handle_logout(self, *args):
        """Handle logout action"""
        if self.logout_dialog:
            self.logout_dialog.dismiss()
        app = MDApp.get_running_app()
        app.auth_service.logout()
        app.root.current = "login"
        toast("Logged out successfully")
        
    def on_kv_post(self, base_widget):
        """Called after KV file is loaded"""
        super().on_kv_post(base_widget)
        self.update_responsive_elements()
