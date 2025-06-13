from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp

class SyncScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Title
        title = Label(
            text='Data Synchronization',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(24)
        )
        layout.add_widget(title)
        
        # Status label
        self.status_label = Label(
            text='Ready to sync',
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.status_label)
        
        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.progress_bar)
        
        # Sync button
        sync_button = Button(
            text='Start Sync',
            size_hint_y=None,
            height=dp(50),
            on_press=self.start_sync
        )
        layout.add_widget(sync_button)
        
        # Add layout to screen
        self.add_widget(layout)
    
    def start_sync(self, instance):
        # Update UI
        self.status_label.text = 'Syncing...'
        self.progress_bar.value = 0
        
        # Schedule sync process
        Clock.schedule_interval(self.update_sync_progress, 0.5)
    
    def update_sync_progress(self, dt):
        # Simulate sync progress
        if self.progress_bar.value < 100:
            self.progress_bar.value += 10
        else:
            self.status_label.text = 'Sync completed'
            return False  # Stop the scheduled event 