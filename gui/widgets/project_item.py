from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import StringProperty

class ProjectItem(BoxLayout):
    project_id = StringProperty('')
    name = StringProperty('')
    description = StringProperty('')
    created_at = StringProperty('')
    sync_status = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = dp(10)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(100)
        
        # Project info
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=0.7
        )
        
        name_label = Label(
            text=self.name,
            size_hint_y=None,
            height=dp(30),
            font_size=dp(18)
        )
        info_layout.add_widget(name_label)
        
        desc_label = Label(
            text=self.description,
            size_hint_y=None,
            height=dp(20),
            font_size=dp(14)
        )
        info_layout.add_widget(desc_label)
        
        date_label = Label(
            text=f"Created: {self.created_at}",
            size_hint_y=None,
            height=dp(20),
            font_size=dp(12)
        )
        info_layout.add_widget(date_label)
        
        self.add_widget(info_layout)
        
        # Action buttons
        actions_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=0.3,
            spacing=dp(5)
        )
        
        edit_btn = Button(
            text='Edit',
            size_hint_y=None,
            height=dp(40),
            on_press=self.edit_project
        )
        actions_layout.add_widget(edit_btn)
        
        delete_btn = Button(
            text='Delete',
            size_hint_y=None,
            height=dp(40),
            on_press=self.delete_project
        )
        actions_layout.add_widget(delete_btn)
        
        self.add_widget(actions_layout)
        
        # Bind properties
        self.bind(name=name_label.setter('text'))
        self.bind(description=desc_label.setter('text'))
        self.bind(created_at=lambda x, v: date_label.setter('text')(x, f"Created: {v}"))
    
    def edit_project(self, instance):
        # TODO: Implement project editing
        pass
    
    def delete_project(self, instance):
        # Get app instance
        app = self.parent.parent.parent.parent.parent
        
        # Delete from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('DELETE FROM projects WHERE id = ?', (self.project_id,))
        app.db_service.conn.commit()
        
        # Queue for sync
        app.sync_service.queue_sync(
            'projects',
            self.project_id,
            'delete',
            None
        )
        
        # Remove from UI
        self.parent.remove_widget(self) 