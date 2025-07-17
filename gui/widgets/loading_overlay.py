from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty

class LoadingOverlay(ModalView):
    """A reusable loading overlay with spinner and message"""
    
    message = StringProperty("Loading...")
    is_visible = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0.5]  # Semi-transparent background
        self.auto_dismiss = False  # Prevent dismissal by tapping outside
        
        # Create the loading card - smaller size for tablets
        self.loading_card = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(160), dp(100)),  # Reduced size
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=8,
            radius=[dp(12)],
            md_bg_color=[1, 1, 1, 1]
        )
        
        # Create the content layout
        content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),  # Reduced spacing
            padding=dp(16),  # Reduced padding
            size_hint=(1, 1)
        )
        
        # Add progress indicator - smaller size
        self.spinner = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(dp(32), dp(32)),  # Smaller spinner
            pos_hint={'center_x': 0.5}
        )
        
        # Add message label - smaller font
        self.message_label = MDLabel(
            text=self.message,
            halign='center',
            theme_text_color="Primary",
            font_size="14sp"  # Smaller font
        )
        
        # Add widgets to layout
        content_layout.add_widget(self.spinner)
        content_layout.add_widget(self.message_label)
        
        # Add layout to card
        self.loading_card.add_widget(content_layout)
        
        # Add card to overlay
        self.add_widget(self.loading_card)
        
        # Bind message property
        self.bind(message=self._on_message_change)
        self.bind(is_visible=self._on_visibility_change)
    
    def _on_message_change(self, instance, value):
        """Update message label when message property changes"""
        if hasattr(self, 'message_label'):
            self.message_label.text = value
    
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