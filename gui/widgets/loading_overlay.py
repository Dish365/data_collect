from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
import os


class LoadingOverlay(ModalView):
    """A reusable loading overlay with spinner and message using KivyMD 2.0.1"""
    
    message = StringProperty("Loading...")
    is_visible = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0.5]  # Semi-transparent background
        self.auto_dismiss = False  # Prevent dismissal by tapping outside
        
        # Delay card creation until after KV files are loaded
        from kivy.clock import Clock
        Clock.schedule_once(self._create_loading_card, 0)
        
        # Bind message property
        self.bind(message=self._on_message_change)
        self.bind(is_visible=self._on_visibility_change)
    
    def _create_loading_card(self, dt):
        """Create the loading card after KV files are loaded"""
        # Create LoadingCard directly - it's defined in KV as LoadingCard@MDCard
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.progressindicator import MDCircularProgressIndicator
        from kivy.metrics import dp
        from kivymd.app import MDApp
        
        # Get the current app to access theme
        app = MDApp.get_running_app()
        
        card = MDCard(
            size_hint=(None, None),
            size=(dp(200), dp(120)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=8,
            radius=[dp(12)],
            md_bg_color=app.theme_cls.surfaceColor if app else [1, 1, 1, 1]
        )
        
        layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(20)
        )
        
        spinner = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            pos_hint={'center_x': 0.5},
            active=True,
            color=app.theme_cls.primaryColor if app else [0, 0, 1, 1]
        )
        
        label = MDLabel(
            text=self.message,
            halign='center',
            theme_text_color='Primary',
            adaptive_height=True,
            size_hint_y=None
        )
        
        layout.add_widget(spinner)
        layout.add_widget(label)
        card.add_widget(layout)
        
        self.loading_card = card
        self.add_widget(card)
    
    def _on_message_change(self, instance, value):
        """Update message label when message property changes"""
        if hasattr(self, 'loading_card'):
            # Try to update KV-loaded LoadingCard first
            if hasattr(self.loading_card, 'message'):
                self.loading_card.message = value
            else:
                # Fallback: find the message label in the card
                for child in self.loading_card.walk():
                    if hasattr(child, 'text') and isinstance(child, object):
                        # Check if this is likely the label (has text property and is a label-like widget)
                        from kivymd.uix.label import MDLabel
                        if isinstance(child, MDLabel):
                            child.text = value
                            break
    
    def _on_visibility_change(self, instance, value):
        """Show/hide overlay when is_visible property changes"""
        if value:
            self.open()
        else:
            self.dismiss()
    
    def show(self, message="Loading..."):
        """Show the loading overlay with optional message"""
        self.message = message
        self.is_visible = True
    
    def hide(self):
        """Hide the loading overlay"""
        self.is_visible = False
    
    def update_message(self, message):
        """Update the loading message"""
        self.message = message 