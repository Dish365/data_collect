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


Builder.load_file("kv/dashboard.kv")


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    
    def navigate_to(self, screen_name):
        self.manager.current = screen_name
    
    def on_enter(self):
        # Update stats when entering screen
        self.ids.top_bar.set_title("Dashboard")
        # self.update_stats()
    
    def update_stats(self):
        # Get app instance
        app = self.manager.get_screen('dashboard').parent
        
        # Update stats from database
        cursor = app.db_service.conn.cursor()
        
        # Total projects
        cursor.execute('SELECT COUNT(*) FROM projects')
        total_projects = cursor.fetchone()[0]
        
        # Active forms
        cursor.execute('SELECT COUNT(*) FROM questions WHERE sync_status = "pending"')
        active_forms = cursor.fetchone()[0]
        
        # Responses today
        cursor.execute('''
            SELECT COUNT(*) FROM responses 
            WHERE date(collected_at) = date('now')
        ''')
        responses_today = cursor.fetchone()[0]
        
        # Pending sync
        cursor.execute('SELECT COUNT(*) FROM sync_queue WHERE status = "pending"')
        pending_sync = cursor.fetchone()[0]
        
        # Update stat cards
        for child in self.children[0].children:
            if isinstance(child, GridLayout):
                for stat_card in child.children:
                    if isinstance(stat_card, StatCard):
                        if stat_card.title == 'Total Projects':
                            stat_card.value = str(total_projects)
                        elif stat_card.title == 'Active Forms':
                            stat_card.value = str(active_forms)
                        elif stat_card.title == 'Responses Today':
                            stat_card.value = str(responses_today)
                        elif stat_card.title == 'Pending Sync':
                            stat_card.value = str(pending_sync) 