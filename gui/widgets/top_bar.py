from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.button import MDButton, MDButtonText
from kivy.core.window import Window
from widgets.responsive_layout import ResponsiveHelper
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

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
    
    def logout(self):
        """Show logout confirmation dialog"""
        if not self.logout_dialog:
            from kivy.uix.widget import Widget
            cancel_button = MDButton(
                MDButtonText(
                    text="Cancel",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                ),
                style="filled",
                on_release=self._dismiss_logout_dialog,
                md_bg_color=(0.4, 0.4, 0.8, 1),
            )
            logout_button = MDButton(
                MDButtonText(
                    text="Yes",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                ),
                style="filled",
                on_release=self._confirm_logout,
                md_bg_color=(1, 0, 0, 1),
            )
            button_container = MDDialogButtonContainer(
                MDBoxLayout(
                    Widget(),
                    cancel_button,
                    logout_button,
                    Widget(),
                    orientation="horizontal",
                    spacing="12dp",
                    size_hint_x=1,
                    pos_hint={"center_x": 0.5}
                )
            )
            self.logout_dialog = MDDialog(
                MDDialogHeadlineText(text="Confirm Logout"),
                MDDialogSupportingText(text="Are you sure you want to logout? All unsaved data will be lost."),
                button_container,
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
        try:
            # Logout from auth service
            if hasattr(app, "auth_service") and app.auth_service:
                app.auth_service.logout()
            app.user_display_name = "Guest"
            MDSnackbar(
                MDSnackbarText(text="Logged out successfully"),
                y=24,
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                md_bg_color="#4CAF50",  # Green for success
                duration=2.5,
            ).open()
            # Navigate back to login screen
            if hasattr(app, "root") and hasattr(app.root, "current"):
                app.root.transition.direction = "right"
                app.root.current = "login"
            else:
                print("Error: app.root or app.root.current not found")
        except Exception as e:
            print(f"Logout error: {e}")
        
    def on_kv_post(self, base_widget):
        """Called after KV file is loaded"""
        super().on_kv_post(base_widget)
        self.update_responsive_elements()
