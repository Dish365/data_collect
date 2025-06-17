from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.lang import Builder
from widgets.project_item import ProjectItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from widgets.project_dialog import ProjectDialog

import uuid

Builder.load_file("kv/projects.kv")



class ProjectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.setup_ui()
    
    # def setup_ui(self):
    #     # Main layout
    #     layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
    #     # Header with title and new project button
    #     header = BoxLayout(
    #         orientation='horizontal',
    #         size_hint_y=None,
    #         height=dp(50)
    #     )
        
    #     title = Label(
    #         text='Projects',
    #         size_hint_x=None,
    #         width=dp(200),
    #         font_size=dp(24)
    #     )
    #     header.add_widget(title)
        
    #     new_project_btn = Button(
    #         text='New Project',
    #         size_hint_x=None,
    #         width=dp(150),
    #         on_press=self.create_new_project
    #     )
    #     header.add_widget(new_project_btn)
        
    #     layout.add_widget(header)
        
    #     # Projects grid
    #     self.projects_grid = GridLayout(
    #         cols=1,
    #         spacing=dp(10),
    #         size_hint_y=None
    #     )
    #     self.projects_grid.bind(minimum_height=self.projects_grid.setter('height'))
        
    #     # Scroll view for projects
    #     scroll = ScrollView()
    #     scroll.add_widget(self.projects_grid)
    #     layout.add_widget(scroll)
        
    #     # Add layout to screen
    #     self.add_widget(layout)
    
    # def on_enter(self):
    #     # Load projects when entering screen
    #     self.load_projects()

    def open_project_dialog(self, is_edit=False, existing_data=None):
        self.dialog_content = ProjectDialog()
        if is_edit and existing_data:
            self.dialog_content.set_data(**existing_data)

        self.dialog = MDDialog(
            title="Edit Project" if is_edit else "New Project",
            type="custom",
            content_cls=self.dialog_content,
            buttons=[
                MDRaisedButton(text="Save", on_release=self.save_project),
                MDRaisedButton(text="Cancel", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()
    
    def save_project(self, instance):
        pass

    def search_projects(self, query):
        query = query.lower()
        for widget in self.ids.projects_grid.children:
            name = widget.name.lower() if hasattr(widget, 'name') else ''
            widget.opacity = 1 if query in name else 0
            widget.disabled = False if query in name else True

    
    def load_projects(self):
        # Clear existing projects
        self.projects_grid.clear_widgets()
        
        # Get app instance
        app = self.manager.get_screen('projects').parent
        
        # Load projects from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            SELECT * FROM projects 
            ORDER BY created_at DESC
        ''')
        projects = cursor.fetchall()
        
        # Add project items
        for project in projects:
            project_item = ProjectItem(
                project_id=project['id'],
                name=project['name'],
                description=project['description'],
                created_at=project['created_at'],
                sync_status=project['sync_status']
            )
            self.projects_grid.add_widget(project_item)
    
    def create_new_project(self, instance):
        # Get app instance
        app = self.manager.get_screen('projects').parent
        
        # Create new project in database
        project_id = str(uuid.uuid4())
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            INSERT INTO projects (id, name, description, created_by)
            VALUES (?, ?, ?, ?)
        ''', (project_id, 'New Project', 'Project description', 'user'))
        app.db_service.conn.commit()
        
        # Queue for sync
        app.sync_service.queue_sync(
            'projects',
            project_id,
            'create',
            {
                'name': 'New Project',
                'description': 'Project description',
                'created_by': 'user'
            }
        )
        
        # Reload projects
        self.load_projects() 