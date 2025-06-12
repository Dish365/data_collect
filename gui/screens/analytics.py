from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from widgets.chart_widget import ChartWidget
import json
import pandas as pd
import numpy as np

class AnalyticsScreen(Screen):
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
            text='Analytics',
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
        
        # Question selector
        selector_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        selector_layout.add_widget(Label(text='Select Question:'))
        self.question_spinner = Spinner(
            text='Select Question',
            values=['Select Question'],
            size_hint_x=None,
            width=dp(300),
            on_text=self.on_question_selected
        )
        selector_layout.add_widget(self.question_spinner)
        layout.add_widget(selector_layout)
        
        # Chart container
        self.chart_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )
        layout.add_widget(self.chart_container)
        
        # Add layout to screen
        self.add_widget(layout)
    
    def on_enter(self):
        # Load projects when entering screen
        self.load_projects()
    
    def load_projects(self):
        # Get app instance
        app = self.manager.get_screen('analytics').parent
        
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
            self.question_spinner.values = ['Select Question']
            self.question_spinner.text = 'Select Question'
            self.chart_container.clear_widgets()
            return
        
        # Get app instance
        app = self.manager.get_screen('analytics').parent
        
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
        
        # Get app instance
        app = self.manager.get_screen('analytics').parent
        
        # Load questions from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            SELECT id, question_text, question_type 
            FROM questions 
            WHERE project_id = ? 
            ORDER BY order_index
        ''', (self.current_project,))
        questions = cursor.fetchall()
        
        # Update question spinner
        self.question_spinner.values = ['Select Question'] + [
            f"{q['question_text']} ({q['question_type']})"
            for q in questions
        ]
        self.question_spinner.text = 'Select Question'
        self.current_questions = questions
    
    def on_question_selected(self, spinner, text):
        if text == 'Select Question':
            self.chart_container.clear_widgets()
            return
        
        # Get selected question
        question_index = self.question_spinner.values.index(text) - 1
        question = self.current_questions[question_index]
        
        # Get app instance
        app = self.manager.get_screen('analytics').parent
        
        # Load responses
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            SELECT response_value 
            FROM responses 
            WHERE question_id = ?
        ''', (question['id'],))
        responses = cursor.fetchall()
        
        # Convert to pandas DataFrame
        df = pd.DataFrame([json.loads(r['response_value']) if question['question_type'] in ['select', 'multiselect'] else r['response_value'] 
                          for r in responses])
        
        # Create appropriate chart
        self.chart_container.clear_widgets()
        
        if question['question_type'] in ['text', 'number']:
            # Show summary statistics
            stats = df.describe()
            chart = ChartWidget(
                chart_type='stats',
                data=stats.to_dict(),
                title=f"Summary Statistics for {question['question_text']}"
            )
        elif question['question_type'] in ['select', 'multiselect']:
            # Show bar chart
            value_counts = df.value_counts()
            chart = ChartWidget(
                chart_type='bar',
                data=value_counts.to_dict(),
                title=f"Response Distribution for {question['question_text']}"
            )
        
        self.chart_container.add_widget(chart) 