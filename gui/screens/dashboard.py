from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from widgets.stat_card import StatCard
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.core.window import Window
from widgets.top_bar import TopBar
from services.dashboard_service import DashboardService
import threading
from kivy.clock import Clock
from widgets.activity_item import ActivityItem
from kivymd.uix.label import MDLabel


Builder.load_file("kv/dashboard.kv")


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.dashboard_service = DashboardService(app.auth_service, app.db_service)

    def on_enter(self, *args):
        """Called when the screen is entered."""
        self.ids.top_bar.set_title("Dashboard")
        self.update_stats()
    
    def navigate_to(self, screen_name):
        self.manager.transition.direction = "left"  
        self.manager.current = screen_name
    
    def show_loader(self, show=True):
        self.ids.spinner.active = show
        self.ids.main_scroll_view.opacity = 0 if show else 1

    def update_stats(self):
        """Fetches dashboard statistics in a background thread."""
        self.show_loader(True)
        threading.Thread(target=self._update_in_thread, daemon=True).start()

    def _update_in_thread(self):
        """Background task to get stats."""
        try:
            stats = self.dashboard_service.get_dashboard_stats()
            Clock.schedule_once(lambda dt: self._update_ui(stats))
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            Clock.schedule_once(lambda dt: self.show_loader(False))

    def _update_ui(self, stats):
        """Updates the UI with new stats."""
        self.ids.total_responses_card.value = stats.get('total_responses', 'N/A')
        self.ids.active_projects_card.value = stats.get('active_projects', 'N/A')
        self.ids.pending_sync_card.value = stats.get('pending_sync', 'N/A')
        self.ids.team_members_card.value = stats.get('team_members', 'N/A')

        activity_feed_layout = self.ids.activity_feed_layout
        activity_feed_layout.clear_widgets()
        activity_feed = stats.get('activity_feed', [])
        
        if not activity_feed:
            activity_feed_layout.add_widget(MDLabel(
                text="No recent activity.", 
                halign="center", 
                theme_text_color="Hint"
            ))
        else:
            for activity in activity_feed:
                activity_feed_layout.add_widget(ActivityItem(
                    activity_text=activity.get('text'),
                    activity_time=activity.get('time'),
                    activity_icon=activity.get('icon')
                ))
        self.show_loader(False) 