"""
Cross-platform toast utility for KivyMD 2.0 compatibility.
Works on Windows, Android, and other platforms.
"""

from kivy.utils import platform
from kivy.clock import Clock
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel


def toast(text, duration=2.5):
    """
    Cross-platform toast notification.
    
    Args:
        text (str): Message to display
        duration (float): Duration in seconds to show the toast
    """
    try:
        if platform == 'android':
            # Try to use native Android toast
            try:
                from kivymd.toast import toast as native_toast
                native_toast(text)
                return
            except ImportError:
                # Fallback to snackbar if native toast fails
                pass
        
        # Use snackbar for all platforms (cross-platform solution)
        def show_snackbar(dt):
            try:
                snackbar = MDSnackbar(
                    MDLabel(
                        text=text,
                        theme_text_color="Custom",
                        text_color="white",
                    ),
                    y=24,
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                    md_bg_color="#323232",
                    radius=[8, 8, 8, 8],
                    duration=duration,
                )
                snackbar.open()
            except Exception as e:
                print(f"Toast error: {e}")
                # Ultimate fallback - just print to console
                print(f"Toast: {text}")
        
        Clock.schedule_once(show_snackbar, 0)
        
    except Exception as e:
        # Ultimate fallback
        print(f"Toast fallback: {text}")


def show_success_toast(text, duration=2.5):
    """Show a success-styled toast."""
    try:
        def show_success_snackbar(dt):
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"✓ {text}",
                    theme_text_color="Custom",
                    text_color="white",
                ),
                y=24,
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                md_bg_color="#4CAF50",  # Green
                radius=[8, 8, 8, 8],
                duration=duration,
            )
            snackbar.open()
        
        Clock.schedule_once(show_success_snackbar, 0)
    except Exception:
        toast(f"✓ {text}", duration)


def show_error_toast(text, duration=3.0):
    """Show an error-styled toast."""
    try:
        def show_error_snackbar(dt):
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"✗ {text}",
                    theme_text_color="Custom",
                    text_color="white",
                ),
                y=24,
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                md_bg_color="#F44336",  # Red
                radius=[8, 8, 8, 8],
                duration=duration,
            )
            snackbar.open()
        
        Clock.schedule_once(show_error_snackbar, 0)
    except Exception:
        toast(f"✗ {text}", duration)


def show_warning_toast(text, duration=2.5):
    """Show a warning-styled toast."""
    try:
        def show_warning_snackbar(dt):
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"⚠ {text}",
                    theme_text_color="Custom",
                    text_color="white",
                ),
                y=24,
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                md_bg_color="#FF9800",  # Orange
                radius=[8, 8, 8, 8],
                duration=duration,
            )
            snackbar.open()
        
        Clock.schedule_once(show_warning_snackbar, 0)
    except Exception:
        toast(f"⚠ {text}", duration) 