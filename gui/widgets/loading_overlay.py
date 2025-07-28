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
        
        # Load the KV file for the UI
        kv_file_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'loading_overlay.kv')
        Builder.load_file(kv_file_path)
        
        # Create the main layout
        self.loading_card = Builder.load_string('''
LoadingCard:
    message: root.message
''')
        
        # Add card to overlay
        self.add_widget(self.loading_card)
        
        # Bind message property
        self.bind(message=self._on_message_change)
        self.bind(is_visible=self._on_visibility_change)
    
    def _on_message_change(self, instance, value):
        """Update message label when message property changes"""
        if hasattr(self, 'loading_card'):
            # Find the message label in the card
            for child in self.loading_card.walk():
                if hasattr(child, 'id') and child.id == 'message_label':
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