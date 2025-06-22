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
    
    def navigate_to(self, screen_name):
        self.manager.transition.direction = "left"  
        self.manager.current = screen_name
    
    def on_enter(self):
        self.ids.top_bar.set_title("Dashboard")
        self.update_stats()
    
    def show_loader(self, show=True):
        self.ids.spinner.active = show
        self.ids.main_scroll_view.opacity = 0 if show else 1

    def update_stats(self):
        self.show_loader(True)
        def _update_in_thread():
            stats = self.dashboard_service.get_dashboard_stats()
            Clock.schedule_once(lambda dt: self._update_ui(stats))

        threading.Thread(target=_update_in_thread).start()

    def _update_ui(self, stats):
        self.ids.total_responses_card.value = stats.get('total_responses', 'N/A')
        self.ids.active_projects_card.value = stats.get('active_projects', 'N/A')
        self.ids.pending_sync_card.value = stats.get('pending_sync', 'N/A')
        self.ids.team_members_card.value = stats.get('team_members', 'N/A')

        # Update activity feed
        activity_feed_layout = self.ids.activity_feed_layout
        activity_feed_layout.clear_widgets()
        activity_feed = stats.get('activity_feed', [])
        
        if not activity_feed:
            no_activity_label = MDLabel(
                text="No recent activity.", 
                halign="center", 
                theme_text_color="Hint"
            )
            activity_feed_layout.add_widget(no_activity_label)
        else:
            for activity in activity_feed:
                item = ActivityItem(
                    activity_text=activity.get('text'),
                    activity_time=activity.get('time'),
                    activity_icon=activity.get('icon')
                )
                activity_feed_layout.add_widget(item)

        self.show_loader(False) 