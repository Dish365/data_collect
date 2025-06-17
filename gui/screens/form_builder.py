from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
import uuid
import json

class FormBuilderScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        self.current_project = None
        self.current_questions = []
    
    def setup_ui(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Header with project selector
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        
        title = Label(
            text='Form Builder',
            size_hint_x=None,
            width=dp(200),
            font_size=dp(24)
        )
        header.add_widget(title)
        
        self.project_spinner = Spinner(
            text='Select Project',
            values=['Select Project'],
            size_hint_x=None,
            width=dp(200),
            on_text=self.on_project_selected
        )
        header.add_widget(self.project_spinner)
        
        layout.add_widget(header)
        
        # Question builder
        builder_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            spacing=dp(10)
        )
        
        # Question type
        type_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        type_layout.add_widget(Label(text='Question Type:'))
        self.type_spinner = Spinner(
            text='Select Type',
            values=['text', 'number', 'select', 'multiselect'],
            size_hint_x=None,
            width=dp(200)
        )
        type_layout.add_widget(self.type_spinner)
        builder_layout.add_widget(type_layout)
        
        # Question text
        text_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        text_layout.add_widget(Label(text='Question Text:'))
        self.question_text = TextInput(
            multiline=False,
            size_hint_x=None,
            width=dp(400)
        )
        text_layout.add_widget(self.question_text)
        builder_layout.add_widget(text_layout)
        
        # Options (for select/multiselect)
        options_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        options_layout.add_widget(Label(text='Options (comma-separated):'))
        self.options_text = TextInput(
            multiline=False,
            size_hint_x=None,
            width=dp(400)
        )
        options_layout.add_widget(self.options_text)
        builder_layout.add_widget(options_layout)
        
        # Add question button
        add_btn = Button(
            text='Add Question',
            size_hint_y=None,
            height=dp(40),
            on_press=self.add_question
        )
        builder_layout.add_widget(add_btn)
        
        layout.add_widget(builder_layout)
        
        # Questions list
        self.questions_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )
        
        # Scroll view for questions
        scroll = ScrollView()
        scroll.add_widget(self.questions_layout)
        layout.add_widget(scroll)
        
        # Add layout to screen
        self.add_widget(layout)
    
    # def on_enter(self):
    #     # Load projects when entering screen
    #     self.load_projects()
    
    def load_projects(self):
        # Get app instance
        app = self.manager.get_screen('form_builder').parent
        
        # Load projects from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('SELECT id, name FROM projects ORDER BY name')
        projects = cursor.fetchall()
        
        # Update spinner values
        self.project_spinner.values = ['Select Project'] + [p['name'] for p in projects]
        self.project_spinner.text = 'Select Project'
    
    def on_project_selected(self, spinner, text):
        if text == 'Select Project':
            self.current_project = None
            self.questions_layout.clear_widgets()
            return
        
        # Get app instance
        app = self.manager.get_screen('form_builder').parent
        
        # Get project ID
        cursor = app.db_service.conn.cursor()
        cursor.execute('SELECT id FROM projects WHERE name = ?', (text,))
        project = cursor.fetchone()
        
        if project:
            self.current_project = project['id']
            self.load_questions()
    
    def load_questions(self):
        if not self.current_project:
            return
        
        # Clear existing questions
        self.questions_layout.clear_widgets()
        self.current_questions = []
        
        # Get app instance
        app = self.manager.get_screen('form_builder').parent
        
        # Load questions from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            SELECT * FROM questions 
            WHERE project_id = ? 
            ORDER BY order_index
        ''', (self.current_project,))
        questions = cursor.fetchall()
        
        # Add question items
        for question in questions:
            self.add_question_item(question)
    
    def add_question(self, instance):
        if not self.current_project:
            return
        
        # Get values
        question_type = self.type_spinner.text
        question_text = self.question_text.text
        options = self.options_text.text
        
        if not question_text:
            return
        
        # Create question
        question_id = str(uuid.uuid4())
        options_json = json.dumps([opt.strip() for opt in options.split(',')]) if options else '[]'
        
        # Get app instance
        app = self.manager.get_screen('form_builder').parent
        
        # Save to database
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            INSERT INTO questions (
                id, project_id, question_text, question_type,
                options, order_index
            )
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            question_id,
            self.current_project,
            question_text,
            question_type,
            options_json,
            len(self.current_questions)
        ))
        app.db_service.conn.commit()
        
        # Queue for sync
        app.sync_service.queue_sync(
            'questions',
            question_id,
            'create',
            {
                'project_id': self.current_project,
                'question_text': question_text,
                'question_type': question_type,
                'options': options_json,
                'order_index': len(self.current_questions)
            }
        )
        
        # Add to UI
        self.add_question_item({
            'id': question_id,
            'question_text': question_text,
            'question_type': question_type,
            'options': options_json
        })
        
        # Clear inputs
        self.question_text.text = ''
        self.options_text.text = ''
    
    def add_question_item(self, question):
        # Create question item
        item = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )
        
        # Question info
        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(
            text=question['question_text'],
            size_hint_y=None,
            height=dp(30)
        ))
        info.add_widget(Label(
            text=f"Type: {question['question_type']}",
            size_hint_y=None,
            height=dp(20)
        ))
        item.add_widget(info)
        
        # Delete button
        delete_btn = Button(
            text='Delete',
            size_hint_x=None,
            width=dp(100),
            on_press=lambda x: self.delete_question(question['id'])
        )
        item.add_widget(delete_btn)
        
        self.questions_layout.add_widget(item)
        self.current_questions.append(item)
    
    def delete_question(self, question_id):
        # Get app instance
        app = self.manager.get_screen('form_builder').parent
        
        # Delete from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        app.db_service.conn.commit()
        
        # Queue for sync
        app.sync_service.queue_sync(
            'questions',
            question_id,
            'delete',
            None
        )
        
        # Reload questions
        self.load_questions() 