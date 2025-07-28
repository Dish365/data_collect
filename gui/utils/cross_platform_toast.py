"""
Cross-platform toast utility for KivyMD 2.0+ compatibility
Provides toast functionality for Windows and other desktop platforms
"""

import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.animation import Animation
from kivy.metrics import dp


class CrossPlatformToast:
    """Cross-platform toast implementation"""
    
    _current_toast = None
    
    @staticmethod
    def toast(text, duration=2.5):
        """
        Show a toast message that works on all platforms
        
        Args:
            text (str): Message to display
            duration (float): Duration in seconds (default: 2.5)
        """
        try:
            # Try to use KivyMD's toast first (for Android)
            if platform.system().lower() == 'linux' and hasattr(platform, 'android'):
                from kivymd.toast import toast as kivymd_toast
                kivymd_toast(text)
                return
        except (ImportError, TypeError):
            pass
        
        # Fallback to custom toast for Windows/Desktop
        CrossPlatformToast._show_desktop_toast(text, duration)
    
    @staticmethod
    def _show_desktop_toast(text, duration):
        """Show custom toast for desktop platforms"""
        try:
            # Remove existing toast if any
            if CrossPlatformToast._current_toast:
                try:
                    Window.remove_widget(CrossPlatformToast._current_toast)
                except:
                    pass
            
            # Create toast widget
            toast_widget = MDCard(
                md_bg_color=(0.2, 0.2, 0.2, 0.9),
                size_hint=(None, None),
                size=(dp(300), dp(50)),
                pos_hint={'center_x': 0.5, 'y': 0.1},
                elevation=8,
                radius=[dp(25)],
                padding=dp(16)
            )
            
            # Add text label
            label = MDLabel(
                text=str(text),
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body1",
                halign="center",
                valign="center"
            )
            
            toast_widget.add_widget(label)
            
            # Add to window
            Window.add_widget(toast_widget)
            CrossPlatformToast._current_toast = toast_widget
            
            # Set initial opacity to 0 for fade-in effect
            toast_widget.opacity = 0
            
            # Animate fade-in
            fade_in = Animation(opacity=1, duration=0.3)
            fade_in.start(toast_widget)
            
            # Schedule removal
            Clock.schedule_once(
                lambda dt: CrossPlatformToast._fade_out_toast(toast_widget), 
                duration
            )
            
        except Exception as e:
            # Ultimate fallback - print to console
            print(f"Toast: {text}")
            print(f"Toast error: {e}")
    
    @staticmethod
    def _fade_out_toast(toast_widget):
        """Fade out and remove toast widget"""
        try:
            # Animate fade-out
            fade_out = Animation(opacity=0, duration=0.3)
            fade_out.bind(on_complete=lambda *args: CrossPlatformToast._remove_toast(toast_widget))
            fade_out.start(toast_widget)
        except:
            CrossPlatformToast._remove_toast(toast_widget)
    
    @staticmethod
    def _remove_toast(toast_widget):
        """Remove toast widget from window"""
        try:
            if toast_widget in Window.children:
                Window.remove_widget(toast_widget)
            if CrossPlatformToast._current_toast == toast_widget:
                CrossPlatformToast._current_toast = None
        except Exception as e:
            print(f"Error removing toast: {e}")


# Main function that replaces kivymd.toast.toast
def toast(text, duration=2.5):
    """
    Cross-platform toast function
    
    Args:
        text (str): Message to display  
        duration (float): Duration in seconds (default: 2.5)
    """
    CrossPlatformToast.toast(text, duration)


# For backwards compatibility
__all__ = ['toast', 'CrossPlatformToast'] 