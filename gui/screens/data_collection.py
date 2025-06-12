from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from widgets.question_widget import QuestionWidget
import uuid

class DataCollectionScreen(Screen):
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
            text='Data Collection',
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
        
        # Questions container
        self.questions_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )
        
        # Scroll view for questions
        scroll = ScrollView()
        scroll.add_widget(self.questions_layout)
        layout.add_widget(scroll)
        
        # Submit button
        submit_btn = Button(
            text='Submit Responses',
            size_hint_y=None,
            height=dp(50),
            on_press=self.submit_responses
        )
        layout.add_widget(submit_btn)
        
        # Add layout to screen
        self.add_widget(layout)
    
    def on_enter(self):
        # Load projects when entering screen
        self.load_projects()
    
    def load_projects(self):
        # Get app instance
        app = self.manager.get_screen('data_collection').parent
        
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
        app = self.manager.get_screen('data_collection').parent
        
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
        app = self.manager.get_screen('data_collection').parent
        
        # Load questions from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            SELECT * FROM questions 
            WHERE project_id = ? 
            ORDER BY order_index
        ''', (self.current_project,))
        questions = cursor.fetchall()
        
        # Add question widgets
        for question in questions:
            question_widget = QuestionWidget(
                question_id=question['id'],
                question_text=question['question_text'],
                question_type=question['question_type'],
                options=question['options']
            )
            self.questions_layout.add_widget(question_widget)
            self.current_questions.append(question_widget)
    
    def submit_responses(self, instance):
        if not self.current_project:
            return
        
        # Get app instance
        app = self.manager.get_screen('data_collection').parent
        
        # Generate respondent ID
        respondent_id = str(uuid.uuid4())
        
        # Save responses
        cursor = app.db_service.conn.cursor()
        for question in self.current_questions:
            response_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO responses (
                    id, project_id, question_id, respondent_id,
                    response_value, collected_by
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                response_id,
                self.current_project,
                question.question_id,
                respondent_id,
                question.get_response(),
                'user'
            ))
            
            # Queue for sync
            app.sync_service.queue_sync(
                'responses',
                response_id,
                'create',
                {
                    'project_id': self.current_project,
                    'question_id': question.question_id,
                    'respondent_id': respondent_id,
                    'response_value': question.get_response(),
                    'collected_by': 'user'
                }
            )
        
        app.db_service.conn.commit()
        
        # Clear responses
        for question in self.current_questions:
            question.clear_response() 