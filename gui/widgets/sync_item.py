from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from datetime import datetime

class SyncItem(MDCard):
    def __init__(self, sync_data, on_sync_pressed=None, **kwargs):
        super().__init__(**kwargs)
        self.sync_data = sync_data
        self.on_sync_pressed = on_sync_pressed
        self.setup_ui()
        
    def setup_ui(self):
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(120)
        self.md_bg_color = (0.95, 0.95, 0.95, 1)
        
        # Main content layout
        content_layout = MDBoxLayout(orientation='horizontal', spacing=dp(12))
        
        # Left side - Item details
        details_layout = MDBoxLayout(orientation='vertical', spacing=dp(4))
        details_layout.size_hint_x = 0.7
        
        # Table name and operation
        table_operation = MDLabel(
            text=f"{self.sync_data['table_name'].title()} - {self.sync_data['operation'].title()}",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(20)
        )
        details_layout.add_widget(table_operation)
        
        # Record ID
        record_id = MDLabel(
            text=f"ID: {self.sync_data['record_id'][:8]}...",
            font_style="Caption",
            size_hint_y=None,
            height=dp(16)
        )
        details_layout.add_widget(record_id)
        
        # Created date
        created_date = self.sync_data.get('created_at', '')
        if created_date:
            try:
                if isinstance(created_date, str):
                    dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    formatted_date = created_date.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = str(created_date)
        else:
            formatted_date = "Unknown"
            
        date_label = MDLabel(
            text=f"Created: {formatted_date}",
            font_style="Caption",
            size_hint_y=None,
            height=dp(16)
        )
        details_layout.add_widget(date_label)
        
        # Attempts
        attempts = self.sync_data.get('attempts', 0)
        attempts_label = MDLabel(
            text=f"Attempts: {attempts}",
            font_style="Caption",
            size_hint_y=None,
            height=dp(16)
        )
        details_layout.add_widget(attempts_label)
        
        content_layout.add_widget(details_layout)
        
        # Right side - Sync button
        button_layout = MDBoxLayout(orientation='vertical', spacing=dp(8))
        button_layout.size_hint_x = 0.3
        
        # Sync button
        sync_button = MDRaisedButton(
            text="Sync",
            size_hint_x=1,
            size_hint_y=None,
            height=dp(36),
            on_press=self.on_sync_button_pressed
        )
        button_layout.add_widget(sync_button)
        
        # Status indicator
        status = self.sync_data.get('status', 'pending')
        status_color = (1, 0.5, 0, 1) if status == 'pending' else (0, 1, 0, 1)
        status_label = MDLabel(
            text=status.title(),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=status_color,
            size_hint_y=None,
            height=dp(16)
        )
        button_layout.add_widget(status_label)
        
        content_layout.add_widget(button_layout)
        
        self.add_widget(content_layout)
    
    def on_sync_button_pressed(self, instance):
        if self.on_sync_pressed:
            self.on_sync_pressed(self.sync_data)
    
    def update_status(self, status):
        """Update the status of this sync item"""
        self.sync_data['status'] = status
        # Refresh the UI
        self.clear_widgets()
        self.setup_ui() 