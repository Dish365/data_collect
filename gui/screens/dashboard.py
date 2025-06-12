from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from widgets.stat_card import StatCard

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Header
        header = Label(
            text='Dashboard',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24)
        )
        layout.add_widget(header)
        
        # Stats grid
        stats_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200)
        )
        
        # Add stat cards
        stats_grid.add_widget(StatCard(
            title='Total Projects',
            value='0',
            icon='folder'
        ))
        stats_grid.add_widget(StatCard(
            title='Active Forms',
            value='0',
            icon='file-document'
        ))
        stats_grid.add_widget(StatCard(
            title='Responses Today',
            value='0',
            icon='chart-bar'
        ))
        stats_grid.add_widget(StatCard(
            title='Pending Sync',
            value='0',
            icon='sync'
        ))
        
        layout.add_widget(stats_grid)
        
        # Quick actions
        actions_label = Label(
            text='Quick Actions',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18)
        )
        layout.add_widget(actions_label)
        
        actions_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200)
        )
        
        # Add action buttons
        actions = [
            ('New Project', 'projects'),
            ('Data Collection', 'data_collection'),
            ('Analytics', 'analytics'),
            ('Form Builder', 'form_builder')
        ]
        
        for text, screen in actions:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(80),
                on_press=lambda x, s=screen: self.navigate_to(s)
            )
            actions_grid.add_widget(btn)
        
        layout.add_widget(actions_grid)
        
        # Add layout to screen
        self.add_widget(layout)
    
    def navigate_to(self, screen_name):
        self.manager.current = screen_name
    
    def on_enter(self):
        # Update stats when entering screen
        self.update_stats()
    
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